import contextlib
from uuid import UUID

from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.integration_repository import IntegrationRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.services.docker_service import DockerService
from domain.services.integration_service import IntegrationService
from domain.services.secret_service import SecretService
from shared.result import Failure, Result, Success


class UninstallMCPUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        integration_repo: IntegrationRepository,
        integration_service: IntegrationService,
        docker: DockerService,
        secret: SecretService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._integration_repo = integration_repo
        self._integration_service = integration_service
        self._docker = docker
        self._secret = secret

    async def execute(self, mcp_id: UUID) -> Result[dict]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        # Stop local gateway if running
        with contextlib.suppress(Exception):
            from infrastructure.mcp.gateway import gateway_manager

            await gateway_manager.stop(mcp_id)

        # Stop and remove Docker container if exists (legacy managed containers)
        if mcp.container_id and not str(mcp.container_id).isdigit():
            with contextlib.suppress(Exception):
                await self._docker.stop_container(mcp.container_id)
            with contextlib.suppress(Exception):
                await self._docker.remove_container(mcp.container_id)

        # Remove credentials from keyring and DB
        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        for cred in creds:
            with contextlib.suppress(Exception):
                await self._secret.delete(cred.keyring_ref)
        await self._credential_repo.delete_by_mcp_id(mcp_id)

        # Disconnect from Cursor config and remove integration records
        with contextlib.suppress(Exception):
            await self._integration_service.disconnect_cursor(mcp)
        await self._integration_repo.delete_by_mcp_id(mcp_id)

        # Delete MCP record
        catalog_id = mcp.catalog_id
        await self._mcp_repo.delete(mcp_id)

        return Success(
            {"message": f"MCP '{catalog_id}' uninstalled successfully", "catalog_id": catalog_id}
        )
