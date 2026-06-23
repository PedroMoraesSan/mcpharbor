"""Resolve how to invoke the Harbor MCP wrapper in dev and bundled sidecar builds."""

from __future__ import annotations

import os
import stat
import sys

from shared.config import is_frozen
from shared.settings import settings

_WRAPPER_BODY = '''\
"""MCP Harbor wrapper — reads credentials from keyring and runs MCP container."""
import os
import sys

from infrastructure.mcp.wrapper_runner import run_wrapper


if __name__ == "__main__":
    run_wrapper(sys.argv[1] if len(sys.argv) > 1 else None)
'''


def wrapper_path() -> str:
    return str(settings.wrapper_bin_dir / "mcpharbour-mcp-wrapper")


def uses_sidecar_cli() -> bool:
    return is_frozen() or os.path.basename(sys.executable).startswith("mcpharbour-api")


def wrapper_command(catalog_id: str) -> tuple[str, list[str]]:
    """Return (executable, args) for spawning the MCP wrapper."""
    if uses_sidecar_cli():
        return sys.executable, ["--run-wrapper", catalog_id]
    return sys.executable, [wrapper_path(), catalog_id]


def install_wrapper_script() -> str:
    """Write/update the on-disk wrapper script and return its path."""
    bin_dir = settings.wrapper_bin_dir
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_file = bin_dir / "mcpharbour-mcp-wrapper"

    if uses_sidecar_cli():
        sidecar = sys.executable
        script = f'#!/usr/bin/env bash\nexec "{sidecar}" --run-wrapper "$1"\n'
        wrapper_file.write_text(script)
    else:
        wrapper_file.write_text(f"#!{sys.executable}\n{_WRAPPER_BODY}")

    wrapper_file.chmod(wrapper_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return str(wrapper_file)
