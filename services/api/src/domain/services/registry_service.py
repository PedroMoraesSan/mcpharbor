from abc import ABC, abstractmethod

from domain.entities.catalog import MCPCatalogEntry


class RegistryService(ABC):
    @abstractmethod
    async def list_catalog(self) -> list[MCPCatalogEntry]: ...

    @abstractmethod
    async def get_by_id(self, catalog_id: str) -> MCPCatalogEntry | None: ...
