from uuid import UUID

from pydantic import BaseModel


class CatalogEntryResponse(BaseModel):
    id: str
    name: str
    description: str
    author: str
    version: str
    docker_image: str
    credentials: list[dict]
    installed: bool


class MCPResponse(BaseModel):
    id: UUID
    catalog_id: str
    name: str
    description: str
    author: str
    version: str
    docker_image: str
    status: str
    container_id: str | None
    container_name: str | None
    has_credentials: bool
    cursor_connected: bool
    local_endpoint: str | None = None
    local_port: int | None = None
    sse_endpoint: str | None = None


class InstallRequest(BaseModel):
    catalog_id: str


class CredentialsRequest(BaseModel):
    credentials: dict[str, str]


class ConnectCursorRequest(BaseModel):
    mcp_id: UUID


class DashboardStatsResponse(BaseModel):
    active_count: int
    error_count: int
    total_count: int
    total_cpu: float
    total_memory_mb: float
    updates_available: int


class MetricsResponse(BaseModel):
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    status: str


class ErrorResponse(BaseModel):
    error: str
    code: str


class SuccessMessageResponse(BaseModel):
    message: str
    config_path: str | None = None


class LocalConnectionInfoResponse(BaseModel):
    mcp_name: str
    catalog_id: str
    docker_image: str
    credential_keys: list[str]
    has_credentials: bool
    wrapper_path: str
    mcp_id: str
    docker_run_command: str
    cursor_json_snippet: str
    claude_json_snippet: str
    vscode_json_snippet: str
    local_endpoint: str | None = None
    sse_endpoint: str | None = None
    gateway_running: bool = False


class SettingsResponse(BaseModel):
    data_dir: str
    cursor_config_path: str
    wrapper_bin_dir: str
    database_kind: str
    database_path: str | None = None
    docker_running: bool
    docker_message: str
    docker_socket: str | None = None
