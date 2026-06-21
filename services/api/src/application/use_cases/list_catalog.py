from application.dto.mcp_dto import MCPDTO, CatalogEntryDTO
from domain.entities.mcp import MCP
from domain.repositories.credential_repository import CredentialRepository
from domain.repositories.mcp_repository import MCPRepository
from domain.services.integration_service import IntegrationService
from domain.services.registry_service import RegistryService
from infrastructure.mcp.gateway import GatewaySession, gateway_manager


class ListCatalogUseCase:
    def __init__(
        self,
        registry: RegistryService,
        mcp_repo: MCPRepository,
    ) -> None:
        self._registry = registry
        self._mcp_repo = mcp_repo

    async def execute(self) -> list[CatalogEntryDTO]:
        catalog = await self._registry.list_catalog()
        installed = await self._mcp_repo.list_all()
        installed_ids = {m.catalog_id for m in installed}

        return [
            CatalogEntryDTO(
                id=entry.id,
                name=entry.name,
                description=entry.description,
                author=entry.author,
                version=entry.version,
                docker_image=entry.docker_image,
                credentials=[
                    {"key": c.key, "label": c.label, "required": c.required}
                    for c in entry.credentials
                ],
                installed=entry.id in installed_ids,
            )
            for entry in catalog
        ]


class ListInstalledMCPsUseCase:
    def __init__(
        self,
        mcp_repo: MCPRepository,
        credential_repo: CredentialRepository,
        integration_service: IntegrationService,
    ) -> None:
        self._mcp_repo = mcp_repo
        self._credential_repo = credential_repo
        self._integration_service = integration_service

    async def execute(self) -> list[MCPDTO]:
        mcps = await self._mcp_repo.list_all()
        result = []
        for mcp in mcps:
            creds = await self._credential_repo.get_by_mcp_id(mcp.id)
            connected = await self._integration_service.is_cursor_connected(mcp.id)
            session = gateway_manager.get(mcp.id)
            result.append(_to_mcp_dto(mcp, bool(creds), connected, session))
        return result


def _to_mcp_dto(
    mcp: MCP,
    has_credentials: bool,
    cursor_connected: bool,
    gateway: GatewaySession | None = None,
) -> MCPDTO:
    return MCPDTO(
        id=mcp.id,
        catalog_id=mcp.catalog_id,
        name=mcp.name,
        description=mcp.description,
        author=mcp.author,
        version=mcp.version,
        docker_image=mcp.docker_image,
        status=mcp.status.value,
        container_id=mcp.container_id,
        container_name=mcp.container_name,
        has_credentials=has_credentials,
        cursor_connected=cursor_connected,
        local_endpoint=gateway.streamable_http_url if gateway else None,
        local_port=gateway.port if gateway else None,
        sse_endpoint=gateway.sse_url if gateway else None,
    )
