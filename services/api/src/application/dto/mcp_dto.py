from dataclasses import dataclass
from uuid import UUID


@dataclass
class CatalogEntryDTO:
    id: str
    name: str
    description: str
    author: str
    version: str
    docker_image: str
    credentials: list[dict]
    installed: bool


@dataclass
class MCPDTO:
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


@dataclass
class DashboardStatsDTO:
    active_count: int
    error_count: int
    total_count: int
    total_cpu: float
    total_memory_mb: float
    updates_available: int


@dataclass
class MetricsDTO:
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    status: str


@dataclass
class InstallProgressDTO:
    status: str
    progress: float
    detail: str


@dataclass
class LocalConnectionInfoDTO:
    mcp_name: str
    catalog_id: str
    docker_image: str
    credential_keys: list[str]
    has_credentials: bool
    wrapper_path: str
    mcp_id: str
    # Pre-rendered snippets
    docker_run_command: str
    cursor_json_snippet: str
    claude_json_snippet: str
    vscode_json_snippet: str
    local_endpoint: str | None = None
    sse_endpoint: str | None = None
    gateway_running: bool = False
