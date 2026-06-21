from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.credential import Credential, Integration
from domain.entities.mcp import MCP
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.integration_repository import IntegrationRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.value_objects.enums import IntegrationClient, MCPStatus
from infrastructure.persistence.models import CredentialModel, InstalledMCPModel, IntegrationModel


def _to_mcp_entity(model: InstalledMCPModel) -> MCP:
    return MCP(
        id=model.id,
        catalog_id=model.catalog_id,
        name=model.name,
        description=model.description,
        author=model.author,
        version=model.version,
        docker_image=model.docker_image,
        status=MCPStatus(model.status),
        container_id=model.container_id,
        container_name=model.container_name,
        installed_at=model.installed_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyMCPRepository(MCPRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, mcp_id: UUID) -> MCP | None:
        result = await self._session.get(InstalledMCPModel, mcp_id)
        return _to_mcp_entity(result) if result else None

    async def get_by_catalog_id(self, catalog_id: str) -> MCP | None:
        stmt = select(InstalledMCPModel).where(InstalledMCPModel.catalog_id == catalog_id)
        result = await self._session.scalar(stmt)
        return _to_mcp_entity(result) if result else None

    async def list_all(self) -> list[MCP]:
        stmt = select(InstalledMCPModel).order_by(InstalledMCPModel.installed_at.desc())
        results = await self._session.scalars(stmt)
        return [_to_mcp_entity(r) for r in results.all()]

    async def save(self, mcp: MCP) -> MCP:
        model = await self._session.get(InstalledMCPModel, mcp.id)
        if model is None:
            model = InstalledMCPModel(id=mcp.id)
            self._session.add(model)

        model.catalog_id = mcp.catalog_id
        model.name = mcp.name
        model.description = mcp.description
        model.author = mcp.author
        model.version = mcp.version
        model.docker_image = mcp.docker_image
        model.status = mcp.status.value
        model.container_id = mcp.container_id
        model.container_name = mcp.container_name
        model.installed_at = mcp.installed_at
        model.updated_at = mcp.updated_at

        await self._session.commit()
        await self._session.refresh(model)
        return _to_mcp_entity(model)

    async def delete(self, mcp_id: UUID) -> None:
        model = await self._session.get(InstalledMCPModel, mcp_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()


class SQLAlchemyCredentialRepository(CredentialRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_mcp_id(self, mcp_id: UUID) -> list[Credential]:
        stmt = select(CredentialModel).where(CredentialModel.mcp_id == mcp_id)
        results = await self._session.scalars(stmt)
        return [
            Credential(
                id=r.id,
                mcp_id=r.mcp_id,
                key_name=r.key_name,
                keyring_ref=r.keyring_ref,
                created_at=r.created_at,
            )
            for r in results.all()
        ]

    async def get_by_mcp_and_key(self, mcp_id: UUID, key_name: str) -> Credential | None:
        stmt = select(CredentialModel).where(
            CredentialModel.mcp_id == mcp_id,
            CredentialModel.key_name == key_name,
        )
        result = await self._session.scalar(stmt)
        if not result:
            return None
        return Credential(
            id=result.id,
            mcp_id=result.mcp_id,
            key_name=result.key_name,
            keyring_ref=result.keyring_ref,
            created_at=result.created_at,
        )

    async def save(self, credential: Credential) -> Credential:
        model = await self._session.get(CredentialModel, credential.id)
        if model is None:
            model = CredentialModel(id=credential.id)
            self._session.add(model)

        model.mcp_id = credential.mcp_id
        model.key_name = credential.key_name
        model.keyring_ref = credential.keyring_ref
        model.created_at = credential.created_at

        await self._session.commit()
        await self._session.refresh(model)
        return Credential(
            id=model.id,
            mcp_id=model.mcp_id,
            key_name=model.key_name,
            keyring_ref=model.keyring_ref,
            created_at=model.created_at,
        )

    async def delete_by_mcp_id(self, mcp_id: UUID) -> None:
        stmt = select(CredentialModel).where(CredentialModel.mcp_id == mcp_id)
        results = await self._session.scalars(stmt)
        for model in results.all():
            await self._session.delete(model)
        await self._session.commit()


class SQLAlchemyIntegrationRepository(IntegrationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_client_and_mcp(
        self, client: IntegrationClient, mcp_id: UUID
    ) -> Integration | None:
        stmt = select(IntegrationModel).where(
            IntegrationModel.client == client.value,
            IntegrationModel.mcp_id == mcp_id,
        )
        result = await self._session.scalar(stmt)
        if not result:
            return None
        return Integration(
            id=result.id,
            client=IntegrationClient(result.client),
            mcp_id=result.mcp_id,
            config_path=result.config_path,
            connected_at=result.connected_at,
        )

    async def list_by_mcp(self, mcp_id: UUID) -> list[Integration]:
        stmt = select(IntegrationModel).where(IntegrationModel.mcp_id == mcp_id)
        results = await self._session.scalars(stmt)
        return [
            Integration(
                id=r.id,
                client=IntegrationClient(r.client),
                mcp_id=r.mcp_id,
                config_path=r.config_path,
                connected_at=r.connected_at,
            )
            for r in results.all()
        ]

    async def delete_by_mcp_id(self, mcp_id: UUID) -> None:
        stmt = select(IntegrationModel).where(IntegrationModel.mcp_id == mcp_id)
        results = await self._session.scalars(stmt)
        for model in results.all():
            await self._session.delete(model)
        await self._session.commit()

    async def save(self, integration: Integration) -> Integration:
        model = await self._session.get(IntegrationModel, integration.id)
        if model is None:
            model = IntegrationModel(id=integration.id)
            self._session.add(model)

        model.client = integration.client.value
        model.mcp_id = integration.mcp_id
        model.config_path = integration.config_path
        model.connected_at = integration.connected_at

        await self._session.commit()
        await self._session.refresh(model)
        return Integration(
            id=model.id,
            client=IntegrationClient(model.client),
            mcp_id=model.mcp_id,
            config_path=model.config_path,
            connected_at=model.connected_at,
        )
