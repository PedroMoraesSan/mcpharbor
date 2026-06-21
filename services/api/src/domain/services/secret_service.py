from abc import ABC, abstractmethod


class SecretService(ABC):
    @abstractmethod
    async def store(self, key: str, value: str) -> str: ...

    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    def make_keyring_ref(self, mcp_id: str, key_name: str) -> str: ...
