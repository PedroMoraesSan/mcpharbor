from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.policy import Agent, AgentPolicy


class AgentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, agent_id: UUID) -> Agent | None: ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> Agent | None: ...

    @abstractmethod
    async def list_all(self) -> list[Agent]: ...

    @abstractmethod
    async def save(self, agent: Agent) -> Agent: ...

    @abstractmethod
    async def delete(self, agent_id: UUID) -> None: ...


class PolicyRepository(ABC):
    @abstractmethod
    async def get_by_agent_id(self, agent_id: str) -> AgentPolicy | None: ...

    @abstractmethod
    async def save(self, policy: AgentPolicy) -> AgentPolicy: ...

    @abstractmethod
    async def delete_by_agent_id(self, agent_id: str) -> None: ...
