import asyncio

import keyring

from domain.services.secret_service import SecretService

SERVICE_NAME = "mcpharbour"


class KeyringSecretService(SecretService):
    async def store(self, key: str, value: str) -> str:
        await asyncio.to_thread(keyring.set_password, SERVICE_NAME, key, value)
        return key

    async def get(self, key: str) -> str | None:
        return await asyncio.to_thread(keyring.get_password, SERVICE_NAME, key)

    async def delete(self, key: str) -> None:
        await asyncio.to_thread(keyring.delete_password, SERVICE_NAME, key)

    def make_keyring_ref(self, mcp_id: str, key_name: str) -> str:
        return f"{mcp_id}:{key_name}"
