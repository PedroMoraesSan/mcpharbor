from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.use_cases.agents import CreateAgentUseCase, DeleteAgentUseCase, ListAgentsUseCase
from application.use_cases.policies import GetPolicyUseCase, UpdatePolicyUseCase
from domain.entities.policy import Agent, AgentPolicy, ServerPolicy, ToolRule
from infrastructure.policy.policy_service import PolicyEvaluationService
from shared.result import Failure, Success


@pytest.mark.asyncio
async def test_list_agents_empty():
    agent_repo = AsyncMock()
    agent_repo.list_all.return_value = []

    use_case = ListAgentsUseCase(agent_repo)
    result = await use_case.execute()

    assert result == []


@pytest.mark.asyncio
async def test_list_agents():
    agent_id = uuid4()
    agent_repo = AsyncMock()
    agent_repo.list_all.return_value = [
        Agent(id=agent_id, name="test-agent", token_hash="abc123")
    ]

    use_case = ListAgentsUseCase(agent_repo)
    result = await use_case.execute()

    assert len(result) == 1
    assert result[0].id == agent_id
    assert result[0].name == "test-agent"


@pytest.mark.asyncio
async def test_create_agent():
    agent_repo = AsyncMock()
    agent_repo.save.side_effect = lambda a: a

    use_case = CreateAgentUseCase(agent_repo)
    result = await use_case.execute("my-cursor")

    assert isinstance(result, Success)
    assert result.value.name == "my-cursor"
    assert result.value.token.startswith("harbour_sk_")
    assert agent_repo.save.called


@pytest.mark.asyncio
async def test_delete_agent_not_found():
    agent_repo = AsyncMock()
    agent_repo.get_by_id.return_value = None

    use_case = DeleteAgentUseCase(agent_repo)
    result = await use_case.execute(uuid4())

    assert isinstance(result, Failure)
    assert result.code == "not_found"


@pytest.mark.asyncio
async def test_delete_agent_success():
    agent_id = uuid4()
    agent_repo = AsyncMock()
    agent_repo.get_by_id.return_value = Agent(id=agent_id, name="x", token_hash="h")
    agent_repo.delete.return_value = None

    use_case = DeleteAgentUseCase(agent_repo)
    result = await use_case.execute(agent_id)

    assert isinstance(result, Success)
    agent_repo.delete.assert_called_once_with(agent_id)


@pytest.mark.asyncio
async def test_get_policy_none():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = None

    use_case = GetPolicyUseCase(policy_repo)
    result = await use_case.execute("agent-1")

    assert isinstance(result, Success)
    assert result.value.allowed_servers is None


@pytest.mark.asyncio
async def test_update_policy():
    policy_repo = AsyncMock()
    policy_repo.save.side_effect = lambda p: p

    use_case = UpdatePolicyUseCase(policy_repo)
    result = await use_case.execute(
        "agent-1",
        [
            {
                "server_id": "github",
                "allowed_tools": [
                    {"tool_name": "create_issue", "allowed_arguments": ["title", "body"]}
                ],
            }
        ],
    )

    assert isinstance(result, Success)
    assert result.value.allowed_servers is not None
    assert result.value.allowed_servers[0]["server_id"] == "github"
    assert result.value.allowed_servers[0]["allowed_tools"][0]["tool_name"] == "create_issue"


@pytest.mark.asyncio
async def test_policy_allows_all_when_no_policy():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = None

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed("agent-1", "github", "create_issue")

    assert result is False


@pytest.mark.asyncio
async def test_policy_allows_all_servers_when_allowed_servers_is_none():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = AgentPolicy(
        agent_id="agent-1", allowed_servers=None
    )

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed("agent-1", "github", "create_issue")

    assert result is True


@pytest.mark.asyncio
async def test_policy_denies_server_not_listed():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = AgentPolicy(
        agent_id="agent-1",
        allowed_servers=[ServerPolicy(server_id="postgres", allowed_tools=None)],
    )

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed("agent-1", "github", "create_issue")

    assert result is False


@pytest.mark.asyncio
async def test_policy_allows_all_tools_when_allowed_tools_is_none():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = AgentPolicy(
        agent_id="agent-1",
        allowed_servers=[ServerPolicy(server_id="github", allowed_tools=None)],
    )

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed("agent-1", "github", "create_issue")

    assert result is True


@pytest.mark.asyncio
async def test_policy_denies_tool_not_listed():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = AgentPolicy(
        agent_id="agent-1",
        allowed_servers=[
            ServerPolicy(
                server_id="github",
                allowed_tools=[ToolRule(tool_name="list_issues")],
            )
        ],
    )

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed("agent-1", "github", "create_issue")

    assert result is False


@pytest.mark.asyncio
async def test_policy_allows_tool_with_any_arguments_when_allowed_arguments_is_none():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = AgentPolicy(
        agent_id="agent-1",
        allowed_servers=[
            ServerPolicy(
                server_id="github",
                allowed_tools=[ToolRule(tool_name="create_issue", allowed_arguments=None)],
            )
        ],
    )

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed("agent-1", "github", "create_issue", {"title": "Fix bug"})

    assert result is True


@pytest.mark.asyncio
async def test_policy_denies_argument_not_allowed():
    policy_repo = AsyncMock()
    policy_repo.get_by_agent_id.return_value = AgentPolicy(
        agent_id="agent-1",
        allowed_servers=[
            ServerPolicy(
                server_id="github",
                allowed_tools=[
                    ToolRule(
                        tool_name="create_issue",
                        allowed_arguments=["title"],
                    )
                ],
            )
        ],
    )

    service = PolicyEvaluationService(policy_repo)
    result = await service.check_tool_allowed(
        "agent-1", "github", "create_issue", {"title": "Fix bug", "body": "details"}
    )

    assert result is False
