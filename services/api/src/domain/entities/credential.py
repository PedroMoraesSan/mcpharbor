from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.value_objects.enums import IntegrationClient
from shared.time import utc_now


@dataclass
class Credential:
    id: UUID
    mcp_id: UUID
    key_name: str
    keyring_ref: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Integration:
    id: UUID
    client: IntegrationClient
    mcp_id: UUID
    config_path: str
    connected_at: datetime = field(default_factory=utc_now)
