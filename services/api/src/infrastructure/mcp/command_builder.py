"""Build stdio commands/env for running MCP servers via the Harbor wrapper."""

from __future__ import annotations

from domain.entities.credential import Credential
from domain.entities.mcp import MCP
from infrastructure.mcp.wrapper_command import wrapper_command


def build_wrapper_env(mcp: MCP, credentials: list[Credential]) -> dict[str, str]:
    env: dict[str, str] = {
        "MCPHARBOR_MCP_ID": str(mcp.id),
        "MCPHARBOR_DOCKER_IMAGE": mcp.docker_image,
    }
    if credentials:
        env["MCPHARBOR_ENV_KEY"] = credentials[0].key_name
    return env


def build_wrapper_stdio(mcp: MCP, credentials: list[Credential]) -> tuple[str, list[str], dict[str, str]]:
    """Return (command, args, env) for spawning the Harbor MCP wrapper."""
    command, args = wrapper_command(mcp.catalog_id)
    return command, args, build_wrapper_env(mcp, credentials)
