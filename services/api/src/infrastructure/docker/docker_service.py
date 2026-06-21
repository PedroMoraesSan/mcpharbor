import asyncio
import json
import queue
import threading
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

import docker
from docker.errors import DockerException, NotFound

from domain.entities.catalog import CredentialField, MCPCatalogEntry
from domain.services.docker_service import (
    ContainerInfo,
    ContainerMetrics,
    DockerService,
    PullProgress,
)
from domain.services.registry_service import RegistryService
from infrastructure.docker.docker_host import DockerUnavailableError, resolve_docker_host
from shared.logging import get_logger

logger = get_logger(__name__)

CATALOG_PATH = Path(__file__).parent.parent / "catalog" / "catalog.json"

DOCKER_UNAVAILABLE_MSG = (
    "Docker is not running. Open Docker Desktop, wait until it is ready, then try again."
)


@dataclass
class DockerStatus:
    running: bool
    message: str
    socket: str | None = None


class JsonRegistryService(RegistryService):
    async def list_catalog(self) -> list[MCPCatalogEntry]:
        return await asyncio.to_thread(self._load_catalog)

    async def get_by_id(self, catalog_id: str) -> MCPCatalogEntry | None:
        catalog = await self.list_catalog()
        return next((e for e in catalog if e.id == catalog_id), None)

    def _load_catalog(self) -> list[MCPCatalogEntry]:
        data = json.loads(CATALOG_PATH.read_text())
        return [
            MCPCatalogEntry(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                author=item["author"],
                version=item["version"],
                docker_image=item["docker_image"],
                credentials=[
                    CredentialField(
                        key=c["key"],
                        label=c["label"],
                        required=c.get("required", True),
                    )
                    for c in item.get("credentials", [])
                ],
            )
            for item in data
        ]


class DockerSDKService(DockerService):
    def __init__(self, docker_host: str | None = None) -> None:
        self._explicit_host = docker_host
        self._resolved_host = resolve_docker_host(docker_host)
        self._client: docker.DockerClient | None = None

    @property
    def socket(self) -> str | None:
        return self._resolved_host

    def _connect(self) -> docker.DockerClient:
        if self._client is not None:
            return self._client

        try:
            if self._resolved_host:
                self._client = docker.DockerClient(base_url=self._resolved_host)
            else:
                self._client = docker.from_env()
            return self._client
        except DockerException as exc:
            self._client = None
            raise DockerUnavailableError(DOCKER_UNAVAILABLE_MSG) from exc

    @property
    def client(self) -> docker.DockerClient:
        return self._connect()

    async def get_status(self) -> DockerStatus:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self._connect().ping)
            return DockerStatus(
                running=True,
                message="Docker is running",
                socket=self._resolved_host,
            )
        except (DockerException, DockerUnavailableError):
            return DockerStatus(
                running=False,
                message=DOCKER_UNAVAILABLE_MSG,
                socket=self._resolved_host,
            )

    async def pull_image(self, image: str) -> AsyncIterator[PullProgress]:
        loop = asyncio.get_running_loop()
        q: queue.Queue[PullProgress | BaseException | None] = queue.Queue()

        def _stream_pull() -> None:
            try:
                pull_iter = self.client.api.pull(image, stream=True, decode=True)
                for line in pull_iter:
                    status = line.get("status", "")
                    progress_detail = line.get("progressDetail") or {}
                    current = progress_detail.get("current", 0)
                    total = progress_detail.get("total", 0)
                    pct = (current / total * 100) if total else 0
                    q.put(PullProgress(status=status, progress=pct, detail=line.get("id", "")))
                q.put(
                    PullProgress(
                        status="complete", progress=100, detail="Image pulled successfully"
                    )
                )
            except (DockerException, DockerUnavailableError) as exc:
                detail = (
                    DOCKER_UNAVAILABLE_MSG if isinstance(exc, DockerUnavailableError) else str(exc)
                )
                q.put(PullProgress(status="error", progress=0, detail=detail))
            except BaseException as exc:
                q.put(exc)
            finally:
                q.put(None)

        threading.Thread(target=_stream_pull, daemon=True).start()

        while True:
            item = await loop.run_in_executor(None, q.get)
            if item is None:
                break
            if isinstance(item, BaseException):
                yield PullProgress(status="error", progress=0, detail=str(item))
                break
            yield item

    async def ensure_image(self, image: str) -> None:
        loop = asyncio.get_running_loop()

        def _image_exists() -> bool:
            try:
                self.client.images.get(image)
                return True
            except NotFound:
                return False

        if await loop.run_in_executor(None, _image_exists):
            return

        async for progress in self.pull_image(image):
            if progress.status == "error":
                raise DockerUnavailableError(
                    progress.detail or f"Failed to pull Docker image {image}"
                )

    async def run_container(
        self,
        image: str,
        name: str,
        env: dict[str, str],
        catalog_id: str | None = None,
    ) -> ContainerInfo:
        loop = asyncio.get_running_loop()

        def _run():
            try:
                existing = self.client.containers.get(name)
                existing.remove(force=True)
            except NotFound:
                pass

            run_kwargs: dict = {
                "image": image,
                "name": name,
                "environment": env,
                "detach": True,
                "stdin_open": True,
                "tty": False,
                "remove": False,
            }
            if catalog_id == "docker":
                run_kwargs["volumes"] = {
                    "/var/run/docker.sock": {
                        "bind": "/var/run/docker.sock",
                        "mode": "rw",
                    }
                }

            container = self.client.containers.run(**run_kwargs)
            return container

        try:
            container = await loop.run_in_executor(None, _run)
        except (DockerException, DockerUnavailableError) as exc:
            if isinstance(exc, DockerUnavailableError):
                message = DOCKER_UNAVAILABLE_MSG
            else:
                message = str(exc)
            raise DockerUnavailableError(message) from exc

        return ContainerInfo(
            container_id=container.id,
            name=container.name,
            status=container.status,
        )

    async def stop_container(self, container_id: str) -> None:
        loop = asyncio.get_running_loop()
        container = await loop.run_in_executor(None, self.client.containers.get, container_id)
        await loop.run_in_executor(None, lambda: container.stop(timeout=10))

    async def restart_container(self, container_id: str) -> None:
        loop = asyncio.get_running_loop()
        container = await loop.run_in_executor(None, self.client.containers.get, container_id)
        await loop.run_in_executor(None, lambda: container.restart(timeout=10))

    async def remove_container(self, container_id: str) -> None:
        loop = asyncio.get_running_loop()
        container = await loop.run_in_executor(None, self.client.containers.get, container_id)
        await loop.run_in_executor(None, lambda: container.remove(force=True))

    async def get_container_logs(self, container_id: str, tail: int = 100) -> AsyncIterator[str]:
        loop = asyncio.get_running_loop()
        container = await loop.run_in_executor(None, self.client.containers.get, container_id)
        q: queue.Queue[bytes | None] = queue.Queue()

        def _stream_to_queue() -> None:
            try:
                for chunk in container.logs(stream=True, follow=True, tail=tail):
                    q.put(chunk)
            finally:
                q.put(None)

        threading.Thread(target=_stream_to_queue, daemon=True).start()

        while True:
            chunk = await loop.run_in_executor(None, q.get)
            if chunk is None:
                break
            yield chunk.decode("utf-8", errors="replace")

    async def get_container_metrics(self, container_id: str) -> ContainerMetrics:
        loop = asyncio.get_running_loop()
        container = await loop.run_in_executor(None, self.client.containers.get, container_id)
        # container.stats() only accepts **kwargs — must use lambda, not positional arg
        stats = await loop.run_in_executor(None, lambda: container.stats(stream=False))

        cpu_percent = self._cpu_percent_from_stats(stats)
        memory_stats = stats.get("memory_stats") or {}
        memory_usage = memory_stats.get("usage", 0) or 0
        memory_limit = memory_stats.get("limit", 0) or 0

        return ContainerMetrics(
            cpu_percent=round(cpu_percent, 2),
            memory_usage_mb=round(memory_usage / (1024 * 1024), 2),
            memory_limit_mb=round(memory_limit / (1024 * 1024), 2) if memory_limit else 0.0,
        )

    @staticmethod
    def _cpu_percent_from_stats(stats: dict) -> float:
        try:
            cpu_stats = stats.get("cpu_stats") or {}
            precpu_stats = stats.get("precpu_stats") or {}
            cpu_usage = (cpu_stats.get("cpu_usage") or {}).get("total_usage", 0)
            precpu_usage = (precpu_stats.get("cpu_usage") or {}).get("total_usage", 0)
            system_usage = cpu_stats.get("system_cpu_usage", 0)
            presystem_usage = precpu_stats.get("system_cpu_usage", 0)
            cpu_delta = cpu_usage - precpu_usage
            system_delta = system_usage - presystem_usage
            cpu_count = cpu_stats.get("online_cpus") or len(
                (cpu_stats.get("cpu_usage") or {}).get("percpu_usage") or [1]
            )
            if system_delta <= 0:
                return 0.0
            return (cpu_delta / system_delta) * cpu_count * 100
        except (TypeError, KeyError, ZeroDivisionError):
            return 0.0

    async def is_running(self) -> bool:
        status = await self.get_status()
        return status.running

    async def get_container_status(self, container_id: str) -> str:
        loop = asyncio.get_running_loop()
        try:
            container = await loop.run_in_executor(None, self.client.containers.get, container_id)
            return container.status
        except NotFound:
            return "not_found"
