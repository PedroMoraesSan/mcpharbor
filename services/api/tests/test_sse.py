from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from infrastructure.mcp.gateway import GatewaySession
from infrastructure.mcp.unified_gateway import UnifiedMcpGateway


@pytest.mark.asyncio
@patch("infrastructure.mcp.unified_gateway.gateway_manager")
async def test_stream_sse_unknown_mcp(mock_gateway_manager):
    mock_gateway_manager.get.return_value = None

    gateway = UnifiedMcpGateway(AsyncMock())
    chunks = [c async for c in gateway.stream_sse(uuid4())]

    assert chunks == []


@pytest.mark.asyncio
@patch("infrastructure.mcp.unified_gateway.gateway_manager")
@patch("infrastructure.mcp.unified_gateway.httpx")
async def test_stream_sse_proxies_lines(mock_httpx, mock_gateway_manager):
    mcp_id = uuid4()
    session = GatewaySession(mcp_id=mcp_id, catalog_id="test", name="test", port=18080, _task=MagicMock())
    mock_gateway_manager.get.return_value = session

    mock_resp = MagicMock()
    mock_resp.aiter_lines = MagicMock(
        return_value=_async_gen(
            "event: endpoint", 'data: /messages/?session_id=abc', 'event: message', 'data: {"ok": true}'
        )
    )

    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_resp

    mock_client = MagicMock()
    mock_client.stream.return_value = mock_cm
    mock_client.__aenter__.return_value = mock_client
    mock_httpx.AsyncClient.return_value = mock_client

    gateway = UnifiedMcpGateway(AsyncMock())
    chunks = [c async for c in gateway.stream_sse(mcp_id)]

    assert 'data: /api/v1/mcp/' in chunks[1]
    assert str(mcp_id) in chunks[1]
    assert '/sse/messages/' in chunks[1]
    assert '{"ok": true}' in chunks[3]


@pytest.mark.asyncio
@patch("infrastructure.mcp.unified_gateway.gateway_manager")
async def test_handle_sse_message_unknown_mcp(mock_gateway_manager):
    mock_gateway_manager.get.return_value = None

    gateway = UnifiedMcpGateway(AsyncMock())
    result = await gateway.handle_sse_message(uuid4(), "sess-1", {"method": "ping"})

    assert result is None


@pytest.mark.asyncio
@patch("infrastructure.mcp.unified_gateway.gateway_manager")
async def test_handle_sse_message_forwards_to_proxy(mock_gateway_manager):
    mcp_id = uuid4()
    session = GatewaySession(mcp_id=mcp_id, catalog_id="test", name="test", port=18081, _task=MagicMock())
    mock_gateway_manager.get.return_value = session

    gateway = UnifiedMcpGateway(AsyncMock())
    with patch.object(gateway, "_client") as mock_client:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_resp)

        result = await gateway.handle_sse_message(mcp_id, "sess-1", {"method": "ping", "id": 1})

        assert result is None
        mock_client.post.assert_called_once()
        args = mock_client.post.call_args
        assert ":18081/messages/?session_id=sess-1" in args[0][0]


async def _async_gen(*args):
    for a in args:
        yield a
