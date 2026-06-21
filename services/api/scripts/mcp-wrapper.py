#!/usr/bin/env python3
"""MCP Harbor wrapper — reads credentials from keyring and runs MCP container."""
import os
import subprocess
import sys

import keyring

SERVICE_NAME = "mcpharbour"
CATALOG = {
    "github": {
        "image": "ghcr.io/github/github-mcp-server",
        "env_key": "GITHUB_PERSONAL_ACCESS_TOKEN",
    }
}


def main():
    catalog_id = sys.argv[1] if len(sys.argv) > 1 else "github"
    config = CATALOG.get(catalog_id)
    if not config:
        print(f"Unknown MCP: {catalog_id}", file=sys.stderr)
        sys.exit(1)

    mcp_id = os.environ.get("MCPHARBOR_MCP_ID", catalog_id)
    keyring_ref = f"{mcp_id}:{config['env_key']}"
    token = keyring.get_password(SERVICE_NAME, keyring_ref)
    if not token:
        print(f"Credential not found for {catalog_id}", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env[config["env_key"]] = token

    cmd = [
        "docker", "run", "-i", "--rm",
        "-e", config["env_key"],
        config["image"],
    ]
    proc = subprocess.Popen(cmd, env=env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(proc.wait())


if __name__ == "__main__":
    main()
