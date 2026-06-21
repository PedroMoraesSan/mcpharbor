"""Run MCP containers with credentials from the OS keychain."""

from __future__ import annotations

import os
import subprocess
import sys

import keyring

SERVICE_NAME = "mcpharbour"


def run_wrapper(catalog_id: str | None = None) -> None:
    catalog = catalog_id or (sys.argv[1] if len(sys.argv) > 1 else "github")
    mcp_id = os.environ.get("MCPHARBOR_MCP_ID", catalog)
    docker_image = os.environ.get("MCPHARBOR_DOCKER_IMAGE")
    env_key = os.environ.get("MCPHARBOR_ENV_KEY")

    if not docker_image:
        print("MCPHARBOR_DOCKER_IMAGE not set", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    if env_key and env_key not in env:
        keyring_ref = f"{mcp_id}:{env_key}"
        token = keyring.get_password(SERVICE_NAME, keyring_ref)
        if not token:
            print(f"Credential not found for {catalog}", file=sys.stderr)
            sys.exit(1)
        env[env_key] = token

    cmd = ["docker", "run", "-i", "--rm"]
    if catalog == "docker":
        cmd += ["-v", "/var/run/docker.sock:/var/run/docker.sock"]
    if env_key:
        cmd += ["-e", env_key]
    cmd.append(docker_image)
    proc = subprocess.Popen(cmd, env=env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(proc.wait())
