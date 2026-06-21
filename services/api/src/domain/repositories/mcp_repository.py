from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.mcp import MCP


class MCPRepository(ABC):
    @abstractmethod
    async def get_by_id(self, mcp_id: UUID) -> MCP | None: ...

    @abstractmethod
    async def get_by_catalog_id(self, catalog_id: str) -> MCP | None: ...

    @abstractmethod
    async def list_all(self) -> list[MCP]: ...

    @abstractmethod
    async def save(self, mcp: MCP) -> MCP: ...

    @abstractmethod
    async def delete(self, mcp_id: UUID) -> None: ...
