from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from infrastructure.mcp.gateway import GatewaySession
from infrastructure.mcp.gpars import authorization_denied, server_unavailable
from infrastructure.mcp.unified_gateway import UnifiedMcpGateway
from shared.errors import AUTHORIZATION_DENIED_CODE, SERVER_UNAVAILABLE_CODE
from shared.errors import AUTHORIZATION_DENIED as GPARS_AUTH_DENIED
from shared.errors import SERVER_UNAVAILABLE as GPARS_SERVER_UNAVAILABLE


class TestGparsHelpers:
    def test_authorization_denied_format(self):
        result = authorization_denied(1, "Tool 'x' not allowed for agent 'a'")
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert result["error"]["code"] == AUTHORIZATION_DENIED_CODE
        assert result["error"]["data"]["gpars_code"] == GPARS_AUTH_DENIED
        assert "not allowed" in result["error"]["message"]

    def test_authorization_denied_no_id(self):
        result = authorization_denied(None, "denied")
        assert result["id"] is None

    def test_server_unavailable_format(self):
        result = server_unavailable(2, "Server filesystem not reachable")
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 2
        assert result["error"]["code"] == SERVER_UNAVAILABLE_CODE
        assert result["error"]["data"]["gpars_code"] == GPARS_SERVER_UNAVAILABLE
        assert "not reachable" in result["error"]["message"]

    def test_server_unavailable_no_id(self):
        result = server_unavailable(None, "unavailable")
        assert result["id"] is None


@pytest.mark.asyncio
async def test_unified_gateway_returns_gpars_auth_denied():
    policy = AsyncMock()
    policy.check_tool_allowed = AsyncMock(return_value=False)

    gateway = UnifiedMcpGateway(policy)
    gateway._tool_map = {"write_file": ("filesystem", uuid4())}

    agent = MagicMock()
    agent.agent_id = "agent-1"
    agent.agent_name = "test-agent"

    result = await gateway.handle_jsonrpc(
        {"method": "tools/call", "params": {"name": "write_file", "arguments": {}}, "id": 1},
        agent,
    )

    assert result["error"]["code"] == AUTHORIZATION_DENIED_CODE
    assert "write_file" in result["error"]["message"]
    assert "test-agent" in result["error"]["message"]
    assert result["error"]["data"]["gpars_code"] == GPARS_AUTH_DENIED


@pytest.mark.asyncio
async def test_unified_gateway_returns_gpars_server_unavailable_for_unknown_tool():
    policy = AsyncMock()
    gateway = UnifiedMcpGateway(policy)

    agent = MagicMock()
    agent.agent_id = "agent-1"

    result = await gateway.handle_jsonrpc(
        {"method": "tools/call", "params": {"name": "nonexistent_tool", "arguments": {}}, "id": 1},
        agent,
    )

    assert result["error"]["code"] == SERVER_UNAVAILABLE_CODE
    assert "nonexistent_tool" in result["error"]["message"]
    assert result["error"]["data"]["gpars_code"] == GPARS_SERVER_UNAVAILABLE


@pytest.mark.asyncio
@patch("infrastructure.mcp.unified_gateway.gateway_manager")
async def test_unified_gateway_no_auth_required_without_agent(mock_gateway_manager):
    mcp_id = uuid4()
    session = GatewaySession(mcp_id=mcp_id, catalog_id="test_server", name="test", port=18999, _task=MagicMock())
    mock_gateway_manager.sessions = {mcp_id: session}

    policy = AsyncMock()
    gateway = UnifiedMcpGateway(policy)
    gateway._tool_map = {"test_tool": ("test_server", mcp_id)}

    with patch.object(gateway, "_call_mcp", AsyncMock(return_value={"result": {"content": [{"type": "text", "text": "ok"}]}})):
        result = await gateway.handle_jsonrpc(
            {"method": "tools/call", "params": {"name": "test_tool", "arguments": {}}, "id": 1},
            None,
        )

    assert "error" not in result
    assert result["result"]["content"][0]["text"] == "ok"
