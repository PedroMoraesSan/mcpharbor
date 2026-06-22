import json

from application.dto.mcp_dto import DashboardStatsDTO, LocalConnectionInfoDTO
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.integration_repository import IntegrationRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.services.integration_service import IntegrationService
from domain.services.registry_service import RegistryService
from domain.services.secret_service import SecretService
from domain.value_objects.enums import IntegrationClient, MCPStatus
from infrastructure.integration.cursor_service import CursorIntegrationService
from infrastructure.mcp.gateway import gateway_manager
from shared.result import Failure, Result, Success
from shared.settings import settings


class ConnectCursorUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        integration_repo: IntegrationRepository,
        integration_service: IntegrationService,
        secret: SecretService,
        registry: RegistryService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._integration_repo = integration_repo
        self._integration_service = integration_service
        self._secret = secret
        self._registry = registry

    async def execute(self, mcp_id) -> Result[dict]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        entry = await self._registry.get_by_id(mcp.catalog_id)
        required_keys = (
            {c.key for c in entry.credentials if c.required} if entry else set()
        )

        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        saved_keys = {c.key_name for c in creds}
        missing = required_keys - saved_keys
        if missing:
            return Failure(
                error=f"Save required credentials first: {', '.join(sorted(missing))}",
                code="missing_credentials",
            )

        for cred in creds:
            if cred.key_name not in required_keys:
                continue
            value = await self._secret.get(cred.keyring_ref)
            if not value:
                return Failure(
                    error=f"Credential '{cred.key_name}' not found in keyring",
                    code="missing_credentials",
                )

        try:
            config_path = await self._integration_service.connect_cursor(
                mcp, [c.key_name for c in creds]
            )
            if isinstance(self._integration_service, CursorIntegrationService):
                existing = await self._integration_repo.get_by_client_and_mcp(
                    IntegrationClient.CURSOR, mcp.id
                )
                record = self._integration_service.create_integration_record(mcp, config_path)
                if existing:
                    record.id = existing.id
                await self._integration_repo.save(record)

            return Success(
                {
                    "config_path": config_path,
                    "message": (
                        "Cursor configured successfully. "
                        "Restart Cursor completely, then check Tools & MCP."
                    ),
                }
            )
        except Exception as e:
            return Failure(error=str(e), code="integration_error")


class GetLocalConnectionInfoUseCase:
    """Returns connection snippets so users can connect to an MCP from any client
    (Cursor, Claude Desktop, VS Code, or custom code) without the desktop app."""

    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo

    async def execute(self, mcp_id) -> Result[LocalConnectionInfoDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        credential_keys = [c.key_name for c in creds] if creds else []
        has_credentials = bool(creds)

        wrapper_path = str(settings.wrapper_bin_dir / "mcpharbour-mcp-wrapper")
        env_vars = {k: f"<{k}>" for k in credential_keys} if credential_keys else {}

        # Docker run command — uses credential placeholders so it is safe to display
        extra_flags = ""
        if mcp.catalog_id == "docker":
            extra_flags = "-v /var/run/docker.sock:/var/run/docker.sock"
        env_flags = " ".join(f'-e {k}="${k}"' for k in credential_keys)
        docker_parts = ["docker run -i --rm"]
        if extra_flags:
            docker_parts.append(extra_flags)
        if env_flags:
            docker_parts.append(env_flags)
        docker_parts.append(mcp.docker_image)
        docker_run = " ".join(docker_parts)

        # MCP JSON server block — reused across all snippet styles
        server_block_wrapper: dict = {
            "command": wrapper_path,
            "args": [mcp.catalog_id],
            "env": {
                "MCPHARBOR_MCP_ID": str(mcp.id),
                "MCPHARBOR_DOCKER_IMAGE": mcp.docker_image,
                **({"MCPHARBOR_ENV_KEY": credential_keys[0]} if credential_keys else {}),
            },
        }

        # Direct docker block (no wrapper, credentials must be set in env)
        docker_args = ["run", "-i", "--rm"]
        if mcp.catalog_id == "docker":
            docker_args += ["-v", "/var/run/docker.sock:/var/run/docker.sock"]
        for k in credential_keys:
            docker_args += ["-e", k]
        docker_args.append(mcp.docker_image)
        server_block_direct: dict = {
            "command": "docker",
            "args": docker_args,
            "env": env_vars,
        }

        cursor_snippet = json.dumps(
            {"mcpServers": {mcp.catalog_id: server_block_wrapper}}, indent=2
        )
        claude_snippet = json.dumps(
            {"mcpServers": {mcp.catalog_id: server_block_wrapper}}, indent=2
        )
        vscode_snippet = json.dumps(
            {
                "mcp": {
                    "servers": {
                        mcp.catalog_id: {
                            "type": "stdio",
                            **server_block_direct,
                        }
                    }
                }
            },
            indent=2,
        )

        session = gateway_manager.get(mcp_id)

        return Success(
            LocalConnectionInfoDTO(
                mcp_name=mcp.name,
                catalog_id=mcp.catalog_id,
                docker_image=mcp.docker_image,
                credential_keys=credential_keys,
                has_credentials=has_credentials,
                wrapper_path=wrapper_path,
                mcp_id=str(mcp.id),
                docker_run_command=docker_run,
                cursor_json_snippet=cursor_snippet,
                claude_json_snippet=claude_snippet,
                vscode_json_snippet=vscode_snippet,
                local_endpoint=session.streamable_http_url if session else None,
                sse_endpoint=session.sse_url if session else None,
                gateway_running=session is not None,
            )
        )


class GetDashboardStatsUseCase:
    def __init__(self, mcp_repo: MCPRepository) -> None:
        self._mcp_repo = mcp_repo

    async def execute(self) -> DashboardStatsDTO:
        mcps = await self._mcp_repo.list_all()
        active = [m for m in mcps if m.status == MCPStatus.RUNNING]
        errors = [m for m in mcps if m.status == MCPStatus.ERROR]

        return DashboardStatsDTO(
            active_count=len(active),
            error_count=len(errors),
            total_count=len(mcps),
            total_cpu=0.0,
            total_memory_mb=0.0,
            updates_available=0,
        )
