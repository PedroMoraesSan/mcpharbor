from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.credential import Integration
from domain.value_objects.enums import IntegrationClient


class IntegrationRepository(ABC):
    @abstractmethod
    async def get_by_client_and_mcp(
        self, client: IntegrationClient, mcp_id: UUID
    ) -> Integration | None: ...

    @abstractmethod
    async def list_by_mcp(self, mcp_id: UUID) -> list[Integration]: ...

    @abstractmethod
    async def delete_by_mcp_id(self, mcp_id: UUID) -> None: ...

    @abstractmethod
    async def save(self, integration: Integration) -> Integration: ...
