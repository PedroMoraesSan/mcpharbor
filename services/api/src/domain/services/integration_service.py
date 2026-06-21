from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.mcp import MCP


class IntegrationService(ABC):
    @abstractmethod
    async def connect_cursor(self, mcp: MCP, credential_keys: list[str] | None = None) -> str: ...

    @abstractmethod
    async def disconnect_cursor(self, mcp: MCP) -> None: ...

    @abstractmethod
    async def install_wrapper(self) -> str: ...

    @abstractmethod
    async def is_cursor_connected(self, mcp_id: UUID) -> bool: ...
