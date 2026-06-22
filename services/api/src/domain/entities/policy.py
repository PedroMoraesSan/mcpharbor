from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from shared.time import utc_now


@dataclass(frozen=True)
class ToolRule:
    tool_name: str
    allowed_arguments: list[str] | None = None


@dataclass(frozen=True)
class ServerPolicy:
    server_id: str
    allowed_tools: list[ToolRule] | None = None


@dataclass(frozen=True)
class AgentPolicy:
    agent_id: str
    allowed_servers: list[ServerPolicy] | None = None


@dataclass
class Agent:
    id: UUID
    name: str
    token_hash: str
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
