import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.credential import Credential, Integration
from domain.entities.mcp import MCP
from domain.entities.policy import Agent, AgentPolicy, ServerPolicy, ToolRule
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.integration_repository import IntegrationRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.repositories.policy_repository import AgentRepository, PolicyRepository
from domain.value_objects.enums import IntegrationClient, MCPStatus
from infrastructure.persistence.models import (
    AgentModel,
    CredentialModel,
    InstalledMCPModel,
    IntegrationModel,
    PolicyModel,
)


def _agent_from_model(model: AgentModel) -> Agent:
    return Agent(
        id=model.id,
        name=model.name,
        token_hash=model.token_hash,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _argument_rules_to_json(rules: list | None) -> list[dict] | None:
    if rules is None:
        return None
    return [
        {
            "arg_name": r.arg_name,
            "match_type": r.match_type,
            "pattern": r.pattern,
        }
        for r in rules
    ]


def _json_to_argument_rules(raw: list | None) -> list | None:
    if raw is None:
        return None
    from domain.entities.policy import ArgumentRule

    rules = []
    for r in raw:
        if isinstance(r, str):
            rules.append(ArgumentRule(arg_name=r, match_type="glob", pattern="*"))
        else:
            rules.append(
                ArgumentRule(
                    arg_name=r.get("arg_name", r.get("allowed_arguments", "")),
                    match_type=r.get("match_type", "glob"),
                    pattern=r.get("pattern", "*"),
                )
            )
    return rules


def _policy_rules_to_json(policy: AgentPolicy) -> str:
    if policy.allowed_servers is None:
        return json.dumps({"allowed_servers": None})
    servers = []
    for s in policy.allowed_servers:
        if s.allowed_tools is None:
            servers.append({"server_id": s.server_id, "allowed_tools": None})
        else:
            tools = [
                {
                    "tool_name": t.tool_name,
                    "argument_rules": _argument_rules_to_json(t.argument_rules),
                }
                for t in s.allowed_tools
            ]
            servers.append({"server_id": s.server_id, "allowed_tools": tools})
    return json.dumps({"allowed_servers": servers})


def _json_to_policy_rules(agent_id: str, raw: str) -> AgentPolicy:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return AgentPolicy(agent_id=agent_id, allowed_servers=None)

    servers_raw = data.get("allowed_servers")
    if servers_raw is None:
        return AgentPolicy(agent_id=agent_id, allowed_servers=None)

    servers = []
    for s in servers_raw:
        tools_raw = s.get("allowed_tools")
        if tools_raw is None:
            servers.append(ServerPolicy(server_id=s["server_id"], allowed_tools=None))
        else:
            tools = [
                ToolRule(
                    tool_name=t["tool_name"],
                    argument_rules=_json_to_argument_rules(
                        t.get("argument_rules") or t.get("allowed_arguments")
                    ),
                )
                for t in tools_raw
            ]
            servers.append(ServerPolicy(server_id=s["server_id"], allowed_tools=tools))
    return AgentPolicy(agent_id=agent_id, allowed_servers=servers)


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


class SQLAlchemyAgentRepository(AgentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, agent_id: UUID) -> Agent | None:
        model = await self._session.get(AgentModel, agent_id)
        return _agent_from_model(model) if model else None

    async def get_by_token_hash(self, token_hash: str) -> Agent | None:
        stmt = select(AgentModel).where(AgentModel.token_hash == token_hash)
        result = await self._session.scalar(stmt)
        return _agent_from_model(result) if result else None

    async def list_all(self) -> list[Agent]:
        stmt = select(AgentModel).order_by(AgentModel.created_at.desc())
        results = await self._session.scalars(stmt)
        return [_agent_from_model(r) for r in results.all()]

    async def save(self, agent: Agent) -> Agent:
        model = await self._session.get(AgentModel, agent.id)
        if model is None:
            model = AgentModel(id=agent.id)
            self._session.add(model)

        model.name = agent.name
        model.token_hash = agent.token_hash
        model.created_at = agent.created_at
        model.updated_at = agent.updated_at

        await self._session.commit()
        await self._session.refresh(model)
        return _agent_from_model(model)

    async def delete(self, agent_id: UUID) -> None:
        model = await self._session.get(AgentModel, agent_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()


class SQLAlchemyPolicyRepository(PolicyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_agent_id(self, agent_id: str) -> AgentPolicy | None:
        stmt = select(PolicyModel).where(PolicyModel.agent_id == agent_id)
        model = await self._session.scalar(stmt)
        if not model:
            return None
        return _json_to_policy_rules(str(model.agent_id), model.rules_json)

    async def save(self, policy: AgentPolicy) -> AgentPolicy:
        agent_uuid = UUID(policy.agent_id)
        model = (
            await self._session.scalar(
                select(PolicyModel).where(PolicyModel.agent_id == agent_uuid)
            )
        )
        if model is None:
            model = PolicyModel(agent_id=agent_uuid)
            self._session.add(model)

        model.rules_json = _policy_rules_to_json(policy)
        await self._session.commit()
        await self._session.refresh(model)
        return _json_to_policy_rules(str(model.agent_id), model.rules_json)

    async def delete_by_agent_id(self, agent_id: str) -> None:
        stmt = select(PolicyModel).where(PolicyModel.agent_id == agent_id)
        model = await self._session.scalar(stmt)
        if model:
            await self._session.delete(model)
            await self._session.commit()
