from collections.abc import AsyncIterator

from application.dto.mcp_dto import MetricsDTO
from domain.repositories.mcp_repository import MCPRepository
from domain.services.docker_service import DockerService
from domain.value_objects.enums import MCPStatus
from infrastructure.mcp.gateway import gateway_manager
from shared.result import Failure, Result, Success


def _is_gateway_mode(mcp) -> bool:
    return bool(mcp.container_name and mcp.container_name.startswith("gateway-"))


class GetMCPLogsUseCase:
    def __init__(self, mcp_repo: MCPRepository, docker: DockerService) -> None:
        self._mcp_repo = mcp_repo
        self._docker = docker

    async def stream(self, mcp_id) -> AsyncIterator[str]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            yield "MCP not found"
            return

        session = gateway_manager.get(mcp_id)
        if session:
            yield f"MCP gateway running on {session.streamable_http_url}"
            yield "Connect your app to this endpoint (Streamable HTTP transport)."
            return

        if not mcp.container_id:
            yield "No container running"
            return

        async for line in self._docker.get_container_logs(mcp.container_id):
            yield line


class GetMCPMetricsUseCase:
    def __init__(self, mcp_repo: MCPRepository, docker: DockerService) -> None:
        self._mcp_repo = mcp_repo
        self._docker = docker

    async def execute(self, mcp_id) -> Result[MetricsDTO]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        if not mcp.container_id:
            return Success(
                MetricsDTO(
                    cpu_percent=0.0,
                    memory_usage_mb=0.0,
                    memory_limit_mb=0.0,
                    status=mcp.status.value,
                )
            )

        if _is_gateway_mode(mcp) or gateway_manager.get(mcp_id):
            session = gateway_manager.get(mcp_id)
            port = session.port if session else mcp.container_id
            return Success(
                MetricsDTO(
                    cpu_percent=0.0,
                    memory_usage_mb=0.0,
                    memory_limit_mb=0.0,
                    status=f"gateway:{port}",
                )
            )

        try:
            metrics = await self._docker.get_container_metrics(mcp.container_id)
            status = await self._docker.get_container_status(mcp.container_id)
            if status in {"exited", "dead", "not_found"} and mcp.status == MCPStatus.RUNNING:
                mcp.status = MCPStatus.STOPPED if status == "exited" else MCPStatus.ERROR
                mcp.container_id = None
                await self._mcp_repo.save(mcp)
            return Success(
                MetricsDTO(
                    cpu_percent=metrics.cpu_percent,
                    memory_usage_mb=metrics.memory_usage_mb,
                    memory_limit_mb=metrics.memory_limit_mb,
                    status=status,
                )
            )
        except Exception:
            return Success(
                MetricsDTO(
                    cpu_percent=0.0,
                    memory_usage_mb=0.0,
                    memory_limit_mb=0.0,
                    status="unavailable",
                )
            )
