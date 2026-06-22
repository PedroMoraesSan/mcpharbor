from uuid import UUID, uuid4

from application.dto.agent_dto import AgentDTO, AgentWithTokenDTO
from domain.entities.policy import Agent
from domain.repositories.policy_repository import AgentRepository
from infrastructure.auth.token_service import generate_token
from shared.result import Failure, Result, Success
from shared.time import utc_now


class ListAgentsUseCase:
    def __init__(self, agent_repo: AgentRepository) -> None:
        self._agent_repo = agent_repo

    async def execute(self) -> list[AgentDTO]:
        agents = await self._agent_repo.list_all()
        return [
            AgentDTO(
                id=a.id,
                name=a.name,
                created_at=a.created_at.isoformat(),
            )
            for a in agents
        ]


class CreateAgentUseCase:
    def __init__(self, agent_repo: AgentRepository) -> None:
        self._agent_repo = agent_repo

    async def execute(self, name: str) -> Result[AgentWithTokenDTO]:
        raw_token, token_hash = generate_token()

        agent = Agent(
            id=uuid4(),
            name=name,
            token_hash=token_hash,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        saved = await self._agent_repo.save(agent)
        return Success(
            AgentWithTokenDTO(
                id=saved.id,
                name=saved.name,
                token=raw_token,
                created_at=saved.created_at.isoformat(),
            )
        )


class DeleteAgentUseCase:
    def __init__(self, agent_repo: AgentRepository) -> None:
        self._agent_repo = agent_repo

    async def execute(self, agent_id: UUID) -> Result[dict]:
        agent = await self._agent_repo.get_by_id(agent_id)
        if not agent:
            return Failure(error="Agent not found", code="not_found")
        await self._agent_repo.delete(agent_id)
        return Success({"message": "Agent deleted"})
