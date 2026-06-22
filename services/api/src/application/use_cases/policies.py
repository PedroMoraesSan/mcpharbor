from dataclasses import dataclass

from domain.entities.policy import AgentPolicy, ServerPolicy, ToolRule
from domain.repositories.policy_repository import PolicyRepository
from shared.result import Failure, Result, Success


@dataclass
class PolicyDTO:
    agent_id: str
    allowed_servers: list[dict] | None = None


class GetPolicyUseCase:
    def __init__(self, policy_repo: PolicyRepository) -> None:
        self._policy_repo = policy_repo

    async def execute(self, agent_id: str) -> Result[PolicyDTO]:
        policy = await self._policy_repo.get_by_agent_id(agent_id)
        if not policy:
            return Success(PolicyDTO(agent_id=agent_id, allowed_servers=None))
        return Success(self._to_dto(policy))

    def _to_dto(self, policy: AgentPolicy) -> PolicyDTO:
        if policy.allowed_servers is None:
            return PolicyDTO(agent_id=policy.agent_id, allowed_servers=None)
        servers = []
        for s in policy.allowed_servers:
            if s.allowed_tools is None:
                servers.append({"server_id": s.server_id, "allowed_tools": None})
            else:
                tools = [
                    {
                        "tool_name": t.tool_name,
                        "allowed_arguments": t.allowed_arguments,
                    }
                    for t in s.allowed_tools
                ]
                servers.append({"server_id": s.server_id, "allowed_tools": tools})
        return PolicyDTO(agent_id=policy.agent_id, allowed_servers=servers)


class UpdatePolicyUseCase:
    def __init__(self, policy_repo: PolicyRepository) -> None:
        self._policy_repo = policy_repo

    async def execute(
        self,
        agent_id: str,
        allowed_servers: list[dict] | None,
    ) -> Result[PolicyDTO]:
        servers = None
        if allowed_servers is not None:
            servers = []
            for s in allowed_servers:
                tools = None
                if s.get("allowed_tools") is not None:
                    tools = [
                        ToolRule(
                            tool_name=t["tool_name"],
                            allowed_arguments=t.get("allowed_arguments"),
                        )
                        for t in s["allowed_tools"]
                    ]
                servers.append(ServerPolicy(server_id=s["server_id"], allowed_tools=tools))

        policy = AgentPolicy(agent_id=agent_id, allowed_servers=servers)
        saved = await self._policy_repo.save(policy)
        dto = GetPolicyUseCase(self._policy_repo)._to_dto(saved)
        return Success(dto)
