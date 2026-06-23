import contextlib

from application.dto.mcp_dto import MCPDTO
from application.use_cases.list_catalog import _to_mcp_dto
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.services.registry_service import RegistryService
from domain.services.secret_service import SecretService
from domain.value_objects.enums import MCPStatus
from infrastructure.mcp.command_builder import build_docker_stdio
from infrastructure.mcp.gateway import gateway_manager
from shared.result import Failure, Result, Success
from shared.time import utc_now


class ExposeMCPUseCase:
    """Start the local Streamable HTTP gateway for an already-running MCP."""

    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        secret: SecretService,
        registry: RegistryService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._secret = secret
        self._registry = registry

    async def execute(self, mcp_id) -> Result[MCPDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        if mcp.status != MCPStatus.RUNNING:
            return Failure(error="Start the MCP before exposing it locally", code="invalid_state")

        existing = gateway_manager.get(mcp_id)
        if existing:
            creds = await self._credential_repo.get_by_mcp_id(mcp_id)
            return Success(_to_mcp_dto(mcp, bool(creds), False, existing))

        entry = await self._registry.get_by_id(mcp.catalog_id)
        required_keys = {c.key for c in entry.credentials if c.required} if entry else set()
        creds = await self._credential_repo.get_by_mcp_id(mcp_id)

        resolved: dict[str, str] = {}
        for cred in creds:
            if cred.key_name not in required_keys:
                continue
            value = await self._secret.get(cred.keyring_ref)
            if not value:
                return Failure(
                    error=f"Credential '{cred.key_name}' not found in keyring",
                    code="missing_credentials",
                )
            resolved[cred.key_name] = value

        try:
            command, args, env = build_docker_stdio(mcp, creds, resolved)
            session = await gateway_manager.start(
                mcp.id, mcp.catalog_id, mcp.name, command, args, env
            )
            mcp.container_id = str(session.port)
            mcp.container_name = f"gateway-{session.port}"
            mcp.updated_at = utc_now()
            saved = await self._mcp_repo.save(mcp)
            return Success(_to_mcp_dto(saved, bool(creds), False, session))
        except Exception as exc:
            with contextlib.suppress(Exception):
                await gateway_manager.stop(mcp_id)
            message = str(exc).strip() or exc.__class__.__name__
            return Failure(error=message, code="gateway_error")
