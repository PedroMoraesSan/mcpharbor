from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class PullProgress:
    status: str
    progress: float
    detail: str = ""


@dataclass
class ContainerInfo:
    container_id: str
    name: str
    status: str


@dataclass
class ContainerMetrics:
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float


class DockerService(ABC):
    @abstractmethod
    async def pull_image(self, image: str) -> AsyncIterator[PullProgress]: ...

    @abstractmethod
    async def ensure_image(self, image: str) -> None: ...

    @abstractmethod
    async def run_container(
        self,
        image: str,
        name: str,
        env: dict[str, str],
        catalog_id: str | None = None,
    ) -> ContainerInfo: ...

    @abstractmethod
    async def stop_container(self, container_id: str) -> None: ...

    @abstractmethod
    async def restart_container(self, container_id: str) -> None: ...

    @abstractmethod
    async def remove_container(self, container_id: str) -> None: ...

    @abstractmethod
    async def get_container_logs(
        self, container_id: str, tail: int = 100
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def get_container_metrics(self, container_id: str) -> ContainerMetrics: ...

    @abstractmethod
    async def is_running(self) -> bool: ...

    @abstractmethod
    async def get_container_status(self, container_id: str) -> str: ...
