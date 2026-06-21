import os
from pathlib import Path


class DockerUnavailableError(Exception):
    """Raised when the Docker daemon is not reachable."""

    def __init__(
        self,
        message: str = "Docker is not running. Start Docker Desktop and try again.",
    ) -> None:
        self.message = message
        super().__init__(message)


def _socket_path(host: str) -> Path | None:
    if not host.startswith("unix://"):
        return None
    return Path(host.removeprefix("unix://"))


def _host_socket_exists(host: str) -> bool:
    path = _socket_path(host)
    return path is not None and path.exists()


def resolve_docker_host(explicit: str | None = None) -> str | None:
    """Resolve Docker socket URL, validating that unix sockets exist."""
    candidates = [
        Path.home() / ".docker" / "run" / "docker.sock",
        Path("/var/run/docker.sock"),
    ]

    for host in (explicit, os.environ.get("DOCKER_HOST")):
        if host and _host_socket_exists(host):
            return host

    for path in candidates:
        if path.exists():
            return f"unix://{path}"

    # Return explicit/env value even if missing — connect will fail with clear error
    if explicit:
        return explicit
    return os.environ.get("DOCKER_HOST")
