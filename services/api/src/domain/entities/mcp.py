from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.value_objects.enums import MCPStatus
from shared.time import utc_now


@dataclass
class MCP:
    id: UUID
    catalog_id: str
    name: str
    description: str
    author: str
    version: str
    docker_image: str
    status: MCPStatus = MCPStatus.STOPPED
    container_id: str | None = None
    container_name: str | None = None
    installed_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def can_start(self) -> bool:
        return self.status in (MCPStatus.STOPPED, MCPStatus.ERROR)

    def can_stop(self) -> bool:
        return self.status in (MCPStatus.RUNNING, MCPStatus.STARTING, MCPStatus.ERROR)
