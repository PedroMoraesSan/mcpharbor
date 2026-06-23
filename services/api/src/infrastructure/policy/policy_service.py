import fnmatch
import re

from domain.entities.policy import AgentPolicy
from domain.repositories.policy_repository import PolicyRepository
from domain.services.policy_service import PolicyService as PolicyServiceABC
from shared.logging import get_logger

logger = get_logger(__name__)


def _arg_value_allowed(value: str, rule) -> bool:
    match rule.match_type:
        case "exact":
            return value == rule.pattern
        case "regex":
            return bool(re.match(rule.pattern, value))
        case "glob":
            return fnmatch.fnmatch(value, rule.pattern)
        case _:
            return fnmatch.fnmatch(value, rule.pattern)


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

        if tool.argument_rules is None:
            return True

        if arguments is None:
            return False

        for arg_name, arg_value in arguments.items():
            rule = next(
                (r for r in tool.argument_rules if r.arg_name == arg_name),
                None,
            )
            if rule is None:
                logger.warning(
                    "policy_denied_argument",
                    agent_id=agent_id,
                    server_id=server_id,
                    tool_name=tool_name,
                    argument=arg_name,
                    reason="not_in_rules",
                )
                return False

            if not _arg_value_allowed(str(arg_value), rule):
                logger.warning(
                    "policy_denied_argument_value",
                    agent_id=agent_id,
                    server_id=server_id,
                    tool_name=tool_name,
                    argument=arg_name,
                    value=arg_value,
                    pattern=rule.pattern,
                    match_type=rule.match_type,
                )
                return False

        return True
