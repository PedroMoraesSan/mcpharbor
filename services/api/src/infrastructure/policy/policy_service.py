from domain.entities.policy import AgentPolicy
from domain.repositories.policy_repository import PolicyRepository
from domain.services.policy_service import PolicyService as PolicyServiceABC
from shared.logging import get_logger

logger = get_logger(__name__)


class PolicyEvaluationService(PolicyServiceABC):
    def __init__(self, policy_repo: PolicyRepository) -> None:
        self._policy_repo = policy_repo

    async def get_policy(self, agent_id: str) -> AgentPolicy | None:
        return await self._policy_repo.get_by_agent_id(agent_id)

    async def check_tool_allowed(
        self,
        agent_id: str,
        server_id: str,
        tool_name: str,
        arguments: dict | None = None,
    ) -> bool:
        policy = await self._policy_repo.get_by_agent_id(agent_id)
        if policy is None:
            return False

        if policy.allowed_servers is None:
            return True

        server = next(
            (s for s in policy.allowed_servers if s.server_id == server_id),
            None,
        )
        if server is None:
            logger.warning(
                "policy_denied_server",
                agent_id=agent_id,
                server_id=server_id,
            )
            return False

        if server.allowed_tools is None:
            return True

        tool = next(
            (t for t in server.allowed_tools if t.tool_name == tool_name),
            None,
        )
        if tool is None:
            logger.warning(
                "policy_denied_tool",
                agent_id=agent_id,
                server_id=server_id,
                tool_name=tool_name,
            )
            return False

        if tool.allowed_arguments is None:
            return True

        if arguments is None:
            return False

        for arg in arguments:
            if arg not in tool.allowed_arguments:
                logger.warning(
                    "policy_denied_argument",
                    agent_id=agent_id,
                    server_id=server_id,
                    tool_name=tool_name,
                    argument=arg,
                )
                return False

        return True
