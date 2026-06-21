from uuid import UUID, uuid4

from domain.entities.credential import Credential
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.services.registry_service import RegistryService
from domain.services.secret_service import SecretService
from shared.result import Failure, Result, Success
from shared.time import utc_now


class SaveCredentialUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        secret: SecretService,
        registry: RegistryService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._secret = secret
        self._registry = registry

    async def execute(self, mcp_id: UUID, credentials: dict[str, str]) -> Result[dict]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        entry = await self._registry.get_by_id(mcp.catalog_id)
        if entry:
            required_keys = {c.key for c in entry.credentials if c.required}
            missing = required_keys - set(credentials.keys())
            if missing:
                return Failure(
                    error=f"Missing required credentials: {', '.join(missing)}",
                    code="validation_error",
                )

        saved_keys = []
        for key_name, value in credentials.items():
            keyring_ref = self._secret.make_keyring_ref(str(mcp_id), key_name)
            await self._secret.store(keyring_ref, value)

            existing = await self._credential_repo.get_by_mcp_and_key(mcp_id, key_name)
            cred = Credential(
                id=existing.id if existing else uuid4(),
                mcp_id=mcp_id,
                key_name=key_name,
                keyring_ref=keyring_ref,
                created_at=existing.created_at if existing else utc_now(),
            )
            await self._credential_repo.save(cred)
            saved_keys.append(key_name)

        return Success({"saved": saved_keys})


class ValidateCredentialsUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        secret: SecretService,
        registry: RegistryService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._secret = secret
        self._registry = registry

    async def execute(self, mcp_id: UUID) -> Result[dict]:
        mcp = await self._mcp_repo.get_by_id(mcp_id)
        if not mcp:
            return Failure(error="MCP not found", code="not_found")

        entry = await self._registry.get_by_id(mcp.catalog_id)
        if not entry:
            return Failure(error="Catalog entry not found", code="not_found")

        creds = await self._credential_repo.get_by_mcp_id(mcp_id)
        saved_keys = {c.key_name for c in creds}
        required = {c.key for c in entry.credentials if c.required}
        missing = required - saved_keys

        valid = True
        for cred in creds:
            value = await self._secret.get(cred.keyring_ref)
            if not value:
                valid = False

        return Success(
            {
                "valid": valid and not missing,
                "missing": list(missing),
                "configured": list(saved_keys),
            }
        )
