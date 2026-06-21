#!/usr/bin/env python3
"""CLI entry point for MCP Harbor API sidecar."""

from __future__ import annotations

import argparse
import logging
import multiprocessing
import sys
import traceback

import uvicorn

from shared.config import API_LOG_FILE, ensure_runtime_environment, ensure_user_config
from shared.settings import settings


def _configure_bootstrap_logging() -> None:
    ensure_runtime_environment()
    ensure_user_config()
    logging.basicConfig(
        filename=API_LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.info("Starting MCP Harbor API sidecar")


def _run_wrapper_mode() -> None:
    ensure_runtime_environment()
    from infrastructure.mcp.wrapper_runner import run_wrapper

    catalog_id = sys.argv[2] if len(sys.argv) > 2 else None
    run_wrapper(catalog_id)


def _run_gateway_mode() -> None:
    """Run mcp-proxy inside the bundled sidecar (PyInstaller cannot use `python -m`)."""
    ensure_runtime_environment()
    sys.argv = ["mcp_proxy", *sys.argv[2:]]
    from mcp_proxy.__main__ import main as mcp_proxy_main

    mcp_proxy_main()


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "--run-wrapper":
        _run_wrapper_mode()
        return

    if len(sys.argv) >= 2 and sys.argv[1] == "--run-gateway":
        _run_gateway_mode()
        return

    _configure_bootstrap_logging()

    parser = argparse.ArgumentParser(description="MCP Harbor API")
    parser.add_argument("--host", default=settings.api_host)
    parser.add_argument("--port", type=int, default=settings.api_port)
    args = parser.parse_args()

    logging.info("Binding API on %s:%s", args.host, args.port)

    try:
        from main import app

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_config=None,
        )
    except Exception:
        logging.exception("Sidecar failed to start")
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
