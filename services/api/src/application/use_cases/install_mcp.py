from collections.abc import AsyncIterator
from uuid import uuid4

from application.dto.mcp_dto import MCPDTO, InstallProgressDTO
from domain.entities.mcp import MCP
from domain.repositories.mcp_repository import MCPRepository
from domain.services.docker_service import DockerService
from domain.services.registry_service import RegistryService
from domain.value_objects.enums import MCPStatus
from shared.result import Failure, Result, Success
from shared.time import utc_now


class InstallMCPUseCase:
    def __init__(
        self,
        registry: RegistryService,
        mcp_repo: MCPRepository,
        docker: DockerService,
    ) -> None:
        self._registry = registry
        self._mcp_repo = mcp_repo
        self._docker = docker

    async def execute(self, catalog_id: str) -> Result[MCPDTO]:
        entry = await self._registry.get_by_id(catalog_id)
        if not entry:
            return Failure(error=f"Catalog entry '{catalog_id}' not found", code="not_found")

        existing = await self._mcp_repo.get_by_catalog_id(catalog_id)
        if existing:
            return Failure(
                error=f"MCP '{catalog_id}' is already installed",
                code="duplicate",
            )

        mcp = MCP(
            id=uuid4(),
            catalog_id=entry.id,
            name=entry.name,
            description=entry.description,
            author=entry.author,
            version=entry.version,
            docker_image=entry.docker_image,
            status=MCPStatus.STOPPED,
            installed_at=utc_now(),
            updated_at=utc_now(),
        )
        saved = await self._mcp_repo.save(mcp)
        return Success(
            MCPDTO(
                id=saved.id,
                catalog_id=saved.catalog_id,
                name=saved.name,
                description=saved.description,
                author=saved.author,
                version=saved.version,
                docker_image=saved.docker_image,
                status=saved.status.value,
                container_id=saved.container_id,
                container_name=saved.container_name,
                has_credentials=False,
                cursor_connected=False,
            )
        )

    async def pull_image(self, catalog_id: str) -> AsyncIterator[InstallProgressDTO]:
        entry = await self._registry.get_by_id(catalog_id)
        if not entry:
            yield InstallProgressDTO(status="error", progress=0, detail="Not found")
            return

        async for progress in self._docker.pull_image(entry.docker_image):
            yield InstallProgressDTO(
                status=progress.status,
                progress=progress.progress,
                detail=progress.detail,
            )
