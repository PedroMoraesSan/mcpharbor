"""Local MCP gateway — bridges stdio MCP servers to HTTP for developer integration."""

from __future__ import annotations

import asyncio
import os
import socket
from contextlib import suppress
from dataclasses import dataclass
from uuid import UUID

from infrastructure.mcp.wrapper_command import build_gateway_argv
from shared.config import is_desktop_mode, ensure_runtime_environment
from shared.logging import get_logger

logger = get_logger(__name__)

PORT_RANGE = range(18000, 19000)
STARTUP_TIMEOUT_SECONDS = 300.0 if is_desktop_mode() else 120.0


@dataclass
class GatewaySession:
    mcp_id: UUID
    port: int
    process: asyncio.subprocess.Process

    @property
    def streamable_http_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/mcp"

    @property
    def sse_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/sse"


class McpGatewayManager:
    """Manages one HTTP gateway subprocess per running MCP."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, GatewaySession] = {}

    def get(self, mcp_id: UUID) -> GatewaySession | None:
        session = self._sessions.get(mcp_id)
        if session and session.process.returncode is not None:
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

    async def _read_stream_tail(self, stream: asyncio.StreamReader | None, limit: int = 4096) -> str:
        if stream is None:
            return ""
        with suppress(asyncio.TimeoutError, ValueError):
            data = await asyncio.wait_for(stream.read(limit), timeout=0.5)
            return data.decode("utf-8", errors="replace").strip()
        return ""

    async def _process_failure_message(self, process: asyncio.subprocess.Process) -> str:
        stderr = await self._read_stream_tail(process.stderr)
        stdout = await self._read_stream_tail(process.stdout)
        detail = stderr or stdout

        if detail:
            for line in reversed(detail.splitlines()):
                stripped = line.strip()
                if stripped and (
                    "Error" in stripped
                    or "error" in stripped
                    or stripped.startswith("Credential")
                ):
                    return stripped

        if process.returncode is not None:
            base = f"MCP gateway process exited with code {process.returncode}"
            return f"{base}: {detail}" if detail else base
        if detail:
            return detail[:500]
        return "MCP gateway failed to start"

    async def _terminate_process(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        with suppress(ProcessLookupError):
            process.terminate()
        try:
            with suppress(ProcessLookupError):
                await asyncio.wait_for(process.wait(), timeout=5)
        except TimeoutError:
            with suppress(ProcessLookupError):
                process.kill()
            with suppress(ProcessLookupError):
                await process.wait()

    async def _wait_for_port(self, port: int, process: asyncio.subprocess.Process) -> None:
        deadline = asyncio.get_running_loop().time() + STARTUP_TIMEOUT_SECONDS
        while asyncio.get_running_loop().time() < deadline:
            if process.returncode is not None:
                raise RuntimeError(await self._process_failure_message(process))

            try:
                _reader, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                return
            except (ConnectionRefusedError, OSError):
                await asyncio.sleep(0.25)

        raise TimeoutError(
            f"MCP gateway did not start within {int(STARTUP_TIMEOUT_SECONDS)} seconds. "
            "Ensure Docker Desktop is running and try again."
        )

    async def start(
        self,
        mcp_id: UUID,
        command: str,
        args: list[str],
        env: dict[str, str],
    ) -> GatewaySession:
        await self.stop(mcp_id)

        port = self._allocate_port()
        cmd = build_gateway_argv(port, env, command, args)
        ensure_runtime_environment()
        subprocess_env = os.environ.copy()
        subprocess_env.update({k: str(v) for k, v in env.items()})

        logger.info("starting_mcp_gateway", mcp_id=str(mcp_id), port=port, command=command)
        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=subprocess_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            await self._wait_for_port(port, process)
        except (RuntimeError, TimeoutError):
            await self._terminate_process(process)
            raise
        except Exception as exc:
            await self._terminate_process(process)
            raise RuntimeError(await self._process_failure_message(process)) from exc

        session = GatewaySession(mcp_id=mcp_id, port=port, process=process)
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

        await self._terminate_process(session.process)

    async def stop_all(self) -> None:
        for mcp_id in list(self._sessions):
            await self.stop(mcp_id)


# Process-wide singleton — gateways are runtime-only (not persisted across API restarts).
gateway_manager = McpGatewayManager()
