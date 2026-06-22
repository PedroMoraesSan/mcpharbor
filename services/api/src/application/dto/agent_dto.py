from dataclasses import dataclass
from uuid import UUID


@dataclass
class AgentDTO:
    id: UUID
    name: str
    created_at: str


@dataclass
class AgentWithTokenDTO:
    id: UUID
    name: str
    token: str
    created_at: str
