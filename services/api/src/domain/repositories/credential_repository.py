from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.credential import Credential


class CredentialRepository(ABC):
    @abstractmethod
    async def get_by_mcp_id(self, mcp_id: UUID) -> list[Credential]: ...

    @abstractmethod
    async def get_by_mcp_and_key(self, mcp_id: UUID, key_name: str) -> Credential | None: ...

    @abstractmethod
    async def save(self, credential: Credential) -> Credential: ...

    @abstractmethod
    async def delete_by_mcp_id(self, mcp_id: UUID) -> None: ...
