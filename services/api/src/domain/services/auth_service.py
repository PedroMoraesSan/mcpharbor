from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentContext:
    agent_id: str
    agent_name: str


class AuthService(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> AgentContext | None: ...
