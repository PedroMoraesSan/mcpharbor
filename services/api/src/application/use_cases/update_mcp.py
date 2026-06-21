import contextlib
from collections.abc import AsyncIterator

from application.dto.mcp_dto import MCPDTO, InstallProgressDTO
from application.use_cases.list_catalog import _to_mcp_dto
from domain.repositories.mcp_repository import MCPRepository
from domain.services.docker_service import DockerService
from domain.services.registry_service import RegistryService
from domain.value_objects.enums import MCPStatus
from shared.result import Failure, Result, Success


class UpdateMCPUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        registry: RegistryService,
        docker: DockerService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._registry = registry
        self._docker = docker

    async def execute(self, mcp_id) -> Result[MCPDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        entry = await self._registry.get_by_id(mcp.catalog_id)
        if entry:
            mcp.docker_image = entry.docker_image
            mcp.version = entry.version

        # Stop running container before pulling new image
        if mcp.container_id:
            with contextlib.suppress(Exception):
                await self._docker.stop_container(mcp.container_id)
            with contextlib.suppress(Exception):
                await self._docker.remove_container(mcp.container_id)
            mcp.container_id = None
            mcp.container_name = None

        mcp.status = MCPStatus.UPDATING
        await self._mcp_repo.save(mcp)

        async for _ in self._docker.pull_image(mcp.docker_image):
            pass

        mcp.status = MCPStatus.STOPPED
        saved = await self._mcp_repo.save(mcp)
        return Success(_to_mcp_dto(saved, True, False))

    async def pull_progress(self, mcp_id) -> AsyncIterator[InstallProgressDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            yield InstallProgressDTO(status="error", progress=0, detail="Not found")
            return

        async for progress in self._docker.pull_image(mcp.docker_image):
            yield InstallProgressDTO(
                status=progress.status,
                progress=progress.progress,
                detail=progress.detail,
            )
