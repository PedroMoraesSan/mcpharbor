from abc import ABC, abstractmethod

from domain.entities.policy import AgentPolicy


class PolicyService(ABC):
    @abstractmethod
    async def get_policy(self, agent_id: str) -> AgentPolicy | None: ...

    @abstractmethod
    async def check_tool_allowed(
        self,
        agent_id: str,
        server_id: str,
        tool_name: str,
        arguments: dict | None = None,
    ) -> bool: ...
