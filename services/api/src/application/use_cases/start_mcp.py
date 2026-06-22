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
from infrastructure.mcp.gateway import gateway_manager
from shared.result import Failure, Result, Success
from shared.time import utc_now


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

        if mcp.status == MCPStatus.RUNNING:
            creds = await self._credential_repo.get_by_mcp_id(mcp_id)
            session = gateway_manager.get(mcp_id)
            return Success(_to_mcp_dto(mcp, bool(creds), False, session))

        if not mcp.can_start():
            return Failure(error=f"Cannot start MCP in status '{mcp.status}'", code="invalid_state")

        entry = await self._registry.get_by_id(mcp.catalog_id)
        required_keys = {c.key for c in entry.credentials if c.required} if entry else set()
        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        missing = required_keys - {c.key_name for c in creds}
        if missing:
            return Failure(
                error=f"Missing required credentials: {', '.join(sorted(missing))}",
                code="missing_credentials",
            )

        mcp.status = MCPStatus.STARTING
        await self._mcp_repo.save(mcp)

        try:
            await self._integration_service.install_wrapper()
            try:
                await self._docker.ensure_image(mcp.docker_image)
            except DockerUnavailableError as exc:
                raise RuntimeError(str(exc)) from exc

            mcp.status = MCPStatus.RUNNING
            mcp.container_id = None
            mcp.container_name = None
            mcp.updated_at = utc_now()
            saved = await self._mcp_repo.save(mcp)
            return Success(_to_mcp_dto(saved, bool(creds), False, None))
        except Exception as e:
            mcp.status = MCPStatus.ERROR
            await self._mcp_repo.save(mcp)
            message = str(e).strip() or e.__class__.__name__
            return Failure(error=message, code="start_error")
