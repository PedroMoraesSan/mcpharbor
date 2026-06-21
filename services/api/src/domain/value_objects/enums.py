from enum import StrEnum


class MCPStatus(StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    UPDATING = "updating"


class IntegrationClient(StrEnum):
    CURSOR = "cursor"
    CLAUDE = "claude"
    OPENCODE = "opencode"
    CLINE = "cline"
