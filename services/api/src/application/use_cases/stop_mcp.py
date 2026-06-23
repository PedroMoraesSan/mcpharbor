from contextlib import suppress

from application.dto.mcp_dto import MCPDTO
from application.use_cases.list_catalog import _to_mcp_dto
from application.use_cases.start_mcp import StartMCPUseCase
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.value_objects.enums import MCPStatus
from infrastructure.mcp.gateway import gateway_manager
from shared.result import Failure, Result, Success
from shared.time import utc_now


class StopMCPUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo

    async def execute(self, mcp_id) -> Result[MCPDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        if not mcp.can_stop():
            return Failure(error=f"Cannot stop MCP in status '{mcp.status}'", code="invalid_state")

        with suppress(Exception):
            await gateway_manager.stop(mcp_id)

        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        mcp.status = MCPStatus.STOPPED
        mcp.container_id = None
        mcp.container_name = None
        mcp.updated_at = utc_now()
        saved = await self._mcp_repo.save(mcp)
        return Success(_to_mcp_dto(saved, bool(creds), False))


class RestartMCPUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        start_use_case: StartMCPUseCase,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._start = start_use_case

    async def execute(self, mcp_id) -> Result[MCPDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        if mcp.status not in (MCPStatus.RUNNING, MCPStatus.ERROR):
            return Failure(
                error=f"Cannot restart MCP in status '{mcp.status}'", code="invalid_state"
            )

        await gateway_manager.stop(mcp_id)
        mcp.status = MCPStatus.STOPPED
        mcp.container_id = None
        mcp.container_name = None
        await self._mcp_repo.save(mcp)
        return await self._start.execute(mcp_id)
