from dataclasses import dataclass, field


@dataclass(frozen=True)
class CredentialField:
    key: str
    label: str
    required: bool = True


@dataclass(frozen=True)
class MCPCatalogEntry:
    id: str
    name: str
    description: str
    author: str
    version: str
    docker_image: str
    credentials: list[CredentialField] = field(default_factory=list)
