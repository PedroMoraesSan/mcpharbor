from uuid import UUID

import httpx

from domain.services.auth_service import AgentContext
from domain.services.policy_service import PolicyService
from infrastructure.mcp.gateway import GatewaySession, gateway_manager
from infrastructure.mcp.gpars import authorization_denied, server_unavailable
from shared.logging import get_logger

logger = get_logger(__name__)

JSONRPC_VERSION = "2.0"

_MCP_HTTP_TIMEOUT = 10.0


class UnifiedMcpGateway:
    def __init__(self, policy_service: PolicyService) -> None:
        self._policy_service = policy_service
        self._client = httpx.AsyncClient(base_url="http://127.0.0.1", timeout=_MCP_HTTP_TIMEOUT)
        self._tool_map: dict[str, tuple[str, UUID]] = {}

    async def stream_sse(self, mcp_id: UUID):
        session = gateway_manager.get(mcp_id)
        if not session:
            return

        async with httpx.AsyncClient(timeout=None) as client, client.stream(
            "GET", f"http://127.0.0.1:{session.port}/sse"
        ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and "/messages/" in line:
                        line = line.replace(
                            "/messages/",
                            f"/api/v1/mcp/{mcp_id}/sse/messages/",
                            1,
                        )
                    yield line + "\n"

    async def handle_sse_message(
        self, mcp_id: UUID, session_id: str, body: dict
    ) -> dict | None:
        session = gateway_manager.get(mcp_id)
        if not session:
            return None

        try:
            resp = await self._client.post(
                f":{session.port}/messages/?session_id={session_id}",
                json=body,
            )
            resp.raise_for_status()
            return None
        except Exception as exc:
            logger.warning(
                "sse_message_failed",
                mcp_id=str(mcp_id),
                session_id=session_id,
                error=str(exc),
            )
            return {"error": str(exc)}

    async def handle_jsonrpc(self, body: dict, agent: AgentContext | None) -> dict:
        method = body.get("method", "")
        params = body.get("params", {})
        req_id = body.get("id")

        if method == "tools/list":
            return await self._handle_list_tools(agent, req_id)
        if method == "tools/call":
            return await self._handle_call_tool(params, agent, req_id)
        if method == "resources/list":
            return await self._handle_list_resources(req_id)
        if method == "prompts/list":
            return self._jsonrpc(req_id, result={"prompts": []})

        return self._jsonrpc_error(req_id, -32601, "Method not found")

    async def _refresh_tool_map(self) -> None:
        self._tool_map.clear()
        for mcp_id, session in gateway_manager.sessions.items():
            try:
                data = await self._call_mcp(
                    session, {"method": "tools/list", "id": 1, "jsonrpc": JSONRPC_VERSION}
                )
                tools = (data or {}).get("result", {}).get("tools", [])
                for tool in tools:
                    name = tool.get("name")
                    if name:
                        self._tool_map[name] = (session.catalog_id, mcp_id)
            except Exception as exc:
                logger.warning(
                    "tool_map_refresh_failed", mcp_id=str(mcp_id), error=str(exc)
                )

    async def _call_mcp(self, session: GatewaySession, body: dict) -> dict | None:
        try:
            resp = await self._client.post(f":{session.port}/mcp", json=body)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning(
                "mcp_call_failed", mcp_id=str(session.mcp_id), port=session.port, error=str(exc)
            )
            return None

    async def _handle_list_tools(
        self, agent: AgentContext | None, req_id: int | str | None
    ) -> dict:
        combined: list[dict] = []
        for mcp_id, session in gateway_manager.sessions.items():
            data = await self._call_mcp(
                session, {"method": "tools/list", "id": 1, "jsonrpc": JSONRPC_VERSION}
            )
            tools = (data or {}).get("result", {}).get("tools", [])
            for tool in tools:
                name = tool.get("name", "")
                if agent:
                    allowed = await self._policy_service.check_tool_allowed(
                        agent_id=agent.agent_id,
                        server_id=session.catalog_id,
                        tool_name=name,
                        arguments=None,
                    )
                    if not allowed:
                        continue
                combined.append(tool)
                self._tool_map[name] = (session.catalog_id, mcp_id)
        return self._jsonrpc(req_id, result={"tools": combined})

    async def _handle_call_tool(
        self, params: dict, agent: AgentContext | None, req_id: int | str | None
    ) -> dict:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if not self._tool_map:
            await self._refresh_tool_map()

        entry = self._tool_map.get(tool_name)
        if not entry:
            return server_unavailable(
                req_id,
                f"Tool '{tool_name}' not found on any available server",
            )

        catalog_id, mcp_id = entry

        if agent:
            allowed = await self._policy_service.check_tool_allowed(
                agent_id=agent.agent_id,
                server_id=catalog_id,
                tool_name=tool_name,
                arguments=arguments,
            )
            if not allowed:
                return authorization_denied(
                    req_id,
                    f"Tool '{tool_name}' is not allowed for agent '{agent.agent_name}'",
                )

        session = gateway_manager.sessions.get(mcp_id)
        if not session:
            return server_unavailable(req_id, "Server has been removed")

        data = await self._call_mcp(session, {
            "method": "tools/call",
            "id": 1,
            "jsonrpc": JSONRPC_VERSION,
            "params": params,
        })
        if data is None:
            return server_unavailable(req_id, f"Server '{catalog_id}' did not respond")

        result = data.get("result", data)
        return self._jsonrpc(req_id, result=result)

    async def _handle_list_resources(self, req_id: int | str | None) -> dict:
        all_resources: list[dict] = []
        for session in gateway_manager.sessions.values():
            data = await self._call_mcp(
                session, {"method": "resources/list", "id": 1, "jsonrpc": JSONRPC_VERSION}
            )
            resources = (data or {}).get("result", {}).get("resources", [])
            all_resources.extend(resources)
        return self._jsonrpc(req_id, result={"resources": all_resources})

    @staticmethod
    def _jsonrpc(req_id: int | str | None, *, result: dict) -> dict:
        return {"jsonrpc": JSONRPC_VERSION, "id": req_id, "result": result}

    @staticmethod
    def _jsonrpc_error(req_id: int | str | None, code: int, message: str) -> dict:
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": req_id,
            "error": {"code": code, "message": message},
        }
