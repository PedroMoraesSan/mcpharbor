"""In-process Streamable HTTP gateway — stdio MCP (Docker) to local HTTP."""

from __future__ import annotations

import asyncio
import os
import socket
from contextlib import AsyncExitStack, suppress
from dataclasses import dataclass, field
from uuid import UUID

import uvicorn
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp_proxy.mcp_server import create_single_instance_routes
from mcp_proxy.proxy_server import create_proxy_server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from shared.config import ensure_runtime_environment
from shared.logging import get_logger

logger = get_logger(__name__)

PORT_RANGE = range(18000, 19000)
STARTUP_TIMEOUT_SECONDS = 120.0


@dataclass
class GatewaySession:
    mcp_id: UUID
    catalog_id: str
    name: str
    port: int
    _task: asyncio.Task[None] = field(repr=False)

    @property
    def streamable_http_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/mcp"

    @property
    def sse_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/sse"


async def _status(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "transport": "streamable-http"})


async def _run_streamable_http_gateway(
    *,
    mcp_id: UUID,
    port: int,
    command: str,
    args: list[str],
    env: dict[str, str],
) -> None:
    ensure_runtime_environment()
    proc_env = os.environ.copy()
    proc_env.update({k: str(v) for k, v in env.items()})

    params = StdioServerParameters(command=command, args=args, env=proc_env)

    try:
        async with AsyncExitStack() as stack:
            logger.info("gateway_step", mcp_id=str(mcp_id), step="stdio_connect")
            _devnull = stack.enter_context(open(os.devnull, "w"))  # noqa: SIM115
            read, write = await stack.enter_async_context(stdio_client(params, errlog=_devnull))
            logger.info("gateway_step", mcp_id=str(mcp_id), step="session_init")
            client = await stack.enter_async_context(ClientSession(read, write))
            logger.info("gateway_step", mcp_id=str(mcp_id), step="proxy_create")
            proxy = await create_proxy_server(client)
            logger.info("gateway_step", mcp_id=str(mcp_id), step="routes_create")

            instance_routes, http_manager = create_single_instance_routes(
                proxy,
                stateless_instance=False,
            )
            logger.info("gateway_step", mcp_id=str(mcp_id), step="http_manager_start")
            await stack.enter_async_context(http_manager.run())

            app = Starlette(
                routes=[Route("/status", _status), *instance_routes],
            )
            app.router.redirect_slashes = False

            config = uvicorn.Config(
                app,
                host="127.0.0.1",
                port=port,
                log_level="warning",
                loop="none",
            )
            server = uvicorn.Server(config)
            await server.serve()
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.error(
            "mcp_gateway_error",
            mcp_id=str(mcp_id),
            port=port,
            error=str(exc),
            exc_info=True,
        )
        raise


class McpGatewayManager:
    """One in-process Streamable HTTP server per running MCP."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, GatewaySession] = {}

    def get(self, mcp_id: UUID) -> GatewaySession | None:
        session = self._sessions.get(mcp_id)
        if session and session._task.done():
            self._sessions.pop(mcp_id, None)
            return None
        return session

    def _allocate_port(self) -> int:
        used = {session.port for session in self._sessions.values()}
        for port in PORT_RANGE:
            if port in used:
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No free port available for MCP gateway (18000–18999)")

    async def _wait_for_port(self, port: int, task: asyncio.Task[None]) -> None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + STARTUP_TIMEOUT_SECONDS
        delay = 0.05

        while loop.time() < deadline:
            if task.done():
                exc = task.exception()
                if exc is not None:
                    message = str(exc).strip() or exc.__class__.__name__
                    raise RuntimeError(message) from exc
                raise RuntimeError("MCP gateway stopped unexpectedly")

            with suppress(ConnectionRefusedError, OSError):
                _reader, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                return

            await asyncio.sleep(delay)
            delay = min(delay * 1.4, 0.4)

        raise TimeoutError(
            f"Streamable HTTP gateway did not start within {int(STARTUP_TIMEOUT_SECONDS)} seconds. "
            "Ensure Docker Desktop is running and try again."
        )

    @property
    def sessions(self) -> dict[UUID, GatewaySession]:
        return dict(self._sessions)

    async def start(
        self,
        mcp_id: UUID,
        catalog_id: str,
        name: str,
        command: str,
        args: list[str],
        env: dict[str, str],
    ) -> GatewaySession:
        await self.stop(mcp_id)

        port = self._allocate_port()
        logger.info(
            "starting_mcp_gateway",
            mcp_id=str(mcp_id),
            port=port,
            command=command,
            transport="streamable-http",
        )

        task = asyncio.create_task(
            _run_streamable_http_gateway(
                mcp_id=mcp_id, port=port, command=command, args=args, env=env
            ),
            name=f"mcp-gateway-{mcp_id}",
        )

        try:
            await self._wait_for_port(port, task)
        except Exception:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            raise

        session = GatewaySession(
            mcp_id=mcp_id, catalog_id=catalog_id, name=name, port=port, _task=task
        )
        self._sessions[mcp_id] = session
        logger.info(
            "mcp_gateway_ready",
            mcp_id=str(mcp_id),
            streamable_http=session.streamable_http_url,
            sse=session.sse_url,
        )
        return session

    async def stop(self, mcp_id: UUID) -> None:
        session = self._sessions.pop(mcp_id, None)
        if not session:
            return

        session._task.cancel()
        with suppress(asyncio.CancelledError):
            await session._task

    async def stop_all(self) -> None:
        for mcp_id in list(self._sessions):
            await self.stop(mcp_id)


gateway_manager = McpGatewayManager()
