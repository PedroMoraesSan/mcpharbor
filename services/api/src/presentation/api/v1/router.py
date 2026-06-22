import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from presentation.api.dependencies import UseCaseContainer, get_use_cases
from presentation.schemas.mcp_schemas import (
    CatalogEntryResponse,
    ConnectCursorRequest,
    CredentialsRequest,
    DashboardStatsResponse,
    InstallRequest,
    LocalConnectionInfoResponse,
    MCPResponse,
    MetricsResponse,
    SettingsResponse,
    SuccessMessageResponse,
)
from shared.config import database_kind
from shared.result import Failure
from shared.settings import settings

router = APIRouter(prefix="/api/v1")


def _handle_result(result):
    if isinstance(result, Failure):
        status_map = {
            "not_found": 404,
            "duplicate": 409,
            "validation_error": 422,
            "missing_credentials": 422,
            "invalid_state": 400,
            "docker_unavailable": 503,
            "docker_error": 503,
            "gateway_error": 503,
            "integration_error": 502,
        }
        raise HTTPException(
            status_code=status_map.get(result.code, 400),
            detail={"error": result.error, "code": result.code},
        )
    return result.value


@router.get("/catalog", response_model=list[CatalogEntryResponse])
async def list_catalog(uc: UseCaseContainer = Depends(get_use_cases)):
    entries = await uc.list_catalog.execute()
    return [CatalogEntryResponse(**e.__dict__) for e in entries]


@router.get("/mcps", response_model=list[MCPResponse])
async def list_mcps(uc: UseCaseContainer = Depends(get_use_cases)):
    mcps = await uc.list_installed.execute()
    return [MCPResponse(**m.__dict__) for m in mcps]


@router.get("/mcps/{mcp_id}", response_model=MCPResponse)
async def get_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    mcps = await uc.list_installed.execute()
    mcp = next((m for m in mcps if m.id == mcp_id), None)
    if not mcp:
        raise HTTPException(status_code=404, detail={"error": "MCP not found", "code": "not_found"})
    return MCPResponse(**mcp.__dict__)


@router.post("/mcps/install", response_model=MCPResponse)
async def install_mcp(body: InstallRequest, uc: UseCaseContainer = Depends(get_use_cases)):
    async for progress in uc.install.pull_image(body.catalog_id):
        if progress.status == "error":
            raise HTTPException(
                status_code=503,
                detail={"error": progress.detail, "code": "docker_unavailable"},
            )
    result = await uc.install.execute(body.catalog_id)
    dto = _handle_result(result)
    return MCPResponse(**dto.__dict__)


@router.post("/mcps/install/stream")
async def install_mcp_stream(body: InstallRequest, uc: UseCaseContainer = Depends(get_use_cases)):
    async def event_generator():
        async for progress in uc.install.pull_image(body.catalog_id):
            yield {"event": "progress", "data": json.dumps(progress.__dict__)}
        result = await uc.install.execute(body.catalog_id)
        if isinstance(result, Failure):
            payload = json.dumps({"error": result.error, "code": result.code})
            yield {"event": "error", "data": payload}
        else:
            yield {"event": "complete", "data": json.dumps(result.value.__dict__, default=str)}

    return EventSourceResponse(event_generator())


async def _refetch_mcp(mcp_id: UUID, uc: UseCaseContainer) -> MCPResponse:
    """Re-fetch full MCP including credential/cursor status after mutations."""
    mcps = await uc.list_installed.execute()
    mcp = next((m for m in mcps if m.id == mcp_id), None)
    if not mcp:
        raise HTTPException(status_code=404, detail={"error": "MCP not found", "code": "not_found"})
    return MCPResponse(**mcp.__dict__)


@router.delete("/mcps/{mcp_id}", response_model=SuccessMessageResponse)
async def uninstall_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.uninstall.execute(mcp_id)
    data = _handle_result(result)
    return SuccessMessageResponse(message=data["message"])


@router.post("/mcps/{mcp_id}/start", response_model=MCPResponse)
async def start_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.start.execute(mcp_id)
    _handle_result(result)
    return await _refetch_mcp(mcp_id, uc)


@router.post("/mcps/{mcp_id}/stop", response_model=MCPResponse)
async def stop_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.stop.execute(mcp_id)
    _handle_result(result)
    return await _refetch_mcp(mcp_id, uc)


@router.post("/mcps/{mcp_id}/expose", response_model=MCPResponse)
async def expose_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.expose.execute(mcp_id)
    _handle_result(result)
    return await _refetch_mcp(mcp_id, uc)


@router.post("/mcps/{mcp_id}/restart", response_model=MCPResponse)
async def restart_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.restart.execute(mcp_id)
    _handle_result(result)
    return await _refetch_mcp(mcp_id, uc)


@router.post("/mcps/{mcp_id}/update", response_model=MCPResponse)
async def update_mcp(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.update.execute(mcp_id)
    _handle_result(result)
    return await _refetch_mcp(mcp_id, uc)


@router.post("/mcps/{mcp_id}/credentials")
async def save_credentials(
    mcp_id: UUID,
    body: CredentialsRequest,
    uc: UseCaseContainer = Depends(get_use_cases),
):
    result = await uc.save_credential.execute(mcp_id, body.credentials)
    return _handle_result(result)


@router.get("/mcps/{mcp_id}/credentials/validate")
async def validate_credentials(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.validate_credentials.execute(mcp_id)
    return _handle_result(result)


@router.get("/mcps/{mcp_id}/metrics", response_model=MetricsResponse)
async def get_metrics(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.metrics.execute(mcp_id)
    dto = _handle_result(result)
    return MetricsResponse(**dto.__dict__)


@router.get("/mcps/{mcp_id}/logs")
async def get_logs(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    async def log_stream():
        async for line in uc.logs.stream(mcp_id):
            yield line

    return StreamingResponse(log_stream(), media_type="text/plain")


@router.get("/mcps/{mcp_id}/logs/stream")
async def stream_logs(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    async def event_generator():
        async for line in uc.logs.stream(mcp_id):
            yield {"event": "log", "data": json.dumps({"line": line})}

    return EventSourceResponse(event_generator())


@router.post("/integrations/cursor/connect", response_model=SuccessMessageResponse)
async def connect_cursor(body: ConnectCursorRequest, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.connect_cursor.execute(body.mcp_id)
    data = _handle_result(result)
    return SuccessMessageResponse(message=data["message"], config_path=data["config_path"])


@router.get("/mcps/{mcp_id}/local-connection", response_model=LocalConnectionInfoResponse)
async def get_local_connection(mcp_id: UUID, uc: UseCaseContainer = Depends(get_use_cases)):
    result = await uc.local_connection.execute(mcp_id)
    dto = _handle_result(result)
    return LocalConnectionInfoResponse(**dto.__dict__)


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def dashboard_stats(uc: UseCaseContainer = Depends(get_use_cases)):
    stats = await uc.dashboard.execute()
    return DashboardStatsResponse(**stats.__dict__)


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(uc: UseCaseContainer = Depends(get_use_cases)):
    status = await uc.docker.get_status()
    return SettingsResponse(
        data_dir=str(settings.data_dir),
        cursor_config_path=str(settings.cursor_config_path),
        wrapper_bin_dir=str(settings.wrapper_bin_dir),
        database_kind=database_kind(settings.database_url),
        database_path=str(settings.database_path) if settings.database_path else None,
        docker_running=status.running,
        docker_message=status.message,
        docker_socket=status.socket,
    )
