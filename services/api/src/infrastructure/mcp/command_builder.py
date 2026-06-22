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


def build_docker_stdio(
    mcp: MCP,
    credentials: list[Credential],
    secrets: dict[str, str] | None = None,
) -> tuple[str, list[str], dict[str, str]]:
    """Return (command, args, env) to spawn the MCP container directly via Docker."""
    env = build_wrapper_env(mcp, credentials)
    if secrets:
        env.update(secrets)

    args = ["run", "-i", "--rm"]
    if mcp.catalog_id == "docker":
        args.extend(["-v", "/var/run/docker.sock:/var/run/docker.sock"])
    for key in secrets or {}:
        args.extend(["-e", key])
    args.append(mcp.docker_image)
    return "docker", args, env


def build_wrapper_stdio(mcp: MCP, credentials: list[Credential]) -> tuple[str, list[str], dict[str, str]]:
    """Return (command, args, env) for spawning the Harbor MCP wrapper."""
    command, args = wrapper_command(mcp.catalog_id)
    return command, args, build_wrapper_env(mcp, credentials)
