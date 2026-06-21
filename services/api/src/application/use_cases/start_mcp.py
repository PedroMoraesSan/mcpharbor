import contextlib

from application.dto.mcp_dto import MCPDTO
from application.use_cases.list_catalog import _to_mcp_dto
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.services.docker_service import DockerService
from domain.services.registry_service import RegistryService
from domain.services.secret_service import SecretService
from domain.value_objects.enums import MCPStatus
from infrastructure.docker.docker_host import DockerUnavailableError
from infrastructure.integration.cursor_service import CursorIntegrationService
from infrastructure.mcp.command_builder import build_wrapper_stdio
from infrastructure.mcp.gateway import gateway_manager
from shared.result import Failure, Result, Success
from shared.time import utc_now


def _format_start_error(exc: Exception) -> str:
    message = str(exc).strip()
    if message:
        return message
    return f"MCP runtime failed to start ({exc.__class__.__name__})"


class StartMCPUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        secret: SecretService,
        registry: RegistryService,
        integration_service: CursorIntegrationService,
        docker: DockerService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._secret = secret
        self._registry = registry
        self._integration_service = integration_service
        self._docker = docker

    async def execute(self, mcp_id) -> Result[MCPDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        if mcp.status == MCPStatus.RUNNING and gateway_manager.get(mcp_id):
            creds = await self._credential_repo.get_by_mcp_id(mcp_id)
            session = gateway_manager.get(mcp_id)
            return Success(_to_mcp_dto(mcp, bool(creds), False, session))

        if not mcp.can_start() and mcp.status != MCPStatus.RUNNING:
            return Failure(error=f"Cannot start MCP in status '{mcp.status}'", code="invalid_state")

        entry = await self._registry.get_by_id(mcp.catalog_id)
        required_keys = (
            {c.key for c in entry.credentials if c.required} if entry else set()
        )

        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        saved_keys = {c.key_name for c in creds}
        missing = required_keys - saved_keys
        if missing:
            return Failure(
                error=f"Missing required credentials: {', '.join(sorted(missing))}",
                code="missing_credentials",
            )

        resolved_credentials: dict[str, str] = {}
        for cred in creds:
            if cred.key_name not in required_keys:
                continue
            value = await self._secret.get(cred.keyring_ref)
            if not value:
                return Failure(
                    error=f"Credential '{cred.key_name}' not found in keyring",
                    code="missing_credentials",
                )
            resolved_credentials[cred.key_name] = value

        mcp.status = MCPStatus.STARTING
        await self._mcp_repo.save(mcp)

        try:
            await self._integration_service.install_wrapper()
            try:
                await self._docker.ensure_image(mcp.docker_image)
            except DockerUnavailableError as exc:
                raise RuntimeError(str(exc)) from exc

            command, args, env = build_wrapper_stdio(mcp, creds)
            env.update(resolved_credentials)
            session = await gateway_manager.start(mcp.id, command, args, env)
            mcp.status = MCPStatus.RUNNING
            mcp.container_id = str(session.port)
            mcp.container_name = f"gateway-{session.port}"
            mcp.updated_at = utc_now()
            saved = await self._mcp_repo.save(mcp)
            return Success(_to_mcp_dto(saved, bool(creds), False, session))
        except Exception as e:
            mcp.status = MCPStatus.ERROR
            await self._mcp_repo.save(mcp)
            with contextlib.suppress(Exception):
                await gateway_manager.stop(mcp_id)
            return Failure(error=_format_start_error(e), code="gateway_error")
