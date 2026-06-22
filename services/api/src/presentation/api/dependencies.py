from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.credentials import SaveCredentialUseCase, ValidateCredentialsUseCase
from application.use_cases.expose_mcp import ExposeMCPUseCase
from application.use_cases.install_mcp import InstallMCPUseCase
from application.use_cases.integrations import ConnectCursorUseCase, GetDashboardStatsUseCase, GetLocalConnectionInfoUseCase
from application.use_cases.list_catalog import ListCatalogUseCase, ListInstalledMCPsUseCase
from application.use_cases.logs_metrics import GetMCPLogsUseCase, GetMCPMetricsUseCase
from application.use_cases.start_mcp import StartMCPUseCase
from application.use_cases.stop_mcp import RestartMCPUseCase, StopMCPUseCase
from application.use_cases.uninstall_mcp import UninstallMCPUseCase
from application.use_cases.update_mcp import UpdateMCPUseCase
from domain.services.docker_service import DockerService
from infrastructure.docker.docker_service import DockerSDKService, JsonRegistryService
from infrastructure.integration.cursor_service import CursorIntegrationService
from infrastructure.keyring.secret_service import KeyringSecretService
from infrastructure.persistence.database import async_session_factory
from infrastructure.persistence.repositories import (
    SQLAlchemyCredentialRepository,
    SQLAlchemyIntegrationRepository,
    SQLAlchemyMCPRepository,
)
from shared.settings import settings


@dataclass
class UseCaseContainer:
    list_catalog: ListCatalogUseCase
    list_installed: ListInstalledMCPsUseCase
    install: InstallMCPUseCase
    uninstall: UninstallMCPUseCase
    start: StartMCPUseCase
    expose: ExposeMCPUseCase
    stop: StopMCPUseCase
    restart: RestartMCPUseCase
    update: UpdateMCPUseCase
    save_credential: SaveCredentialUseCase
    validate_credentials: ValidateCredentialsUseCase
    logs: GetMCPLogsUseCase
    metrics: GetMCPMetricsUseCase
    connect_cursor: ConnectCursorUseCase
    local_connection: GetLocalConnectionInfoUseCase
    dashboard: GetDashboardStatsUseCase
    docker: DockerService


def build_container(session: AsyncSession) -> UseCaseContainer:
    mcp_repo = SQLAlchemyMCPRepository(session)
    credential_repo = SQLAlchemyCredentialRepository(session)
    integration_repo = SQLAlchemyIntegrationRepository(session)
    registry = JsonRegistryService()
    docker = DockerSDKService(settings.docker_host)
    secret = KeyringSecretService()
    integration = CursorIntegrationService()
    start = StartMCPUseCase(mcp_repo, credential_repo, secret, registry, integration, docker)

    return UseCaseContainer(
        list_catalog=ListCatalogUseCase(registry, mcp_repo),
        list_installed=ListInstalledMCPsUseCase(mcp_repo, credential_repo, integration),
        install=InstallMCPUseCase(registry, mcp_repo, docker),
        uninstall=UninstallMCPUseCase(
            mcp_repo, credential_repo, integration_repo, integration, docker, secret
        ),
        start=start,
        expose=ExposeMCPUseCase(mcp_repo, credential_repo, secret, registry),
        stop=StopMCPUseCase(mcp_repo, credential_repo),
        restart=RestartMCPUseCase(mcp_repo, start),
        update=UpdateMCPUseCase(mcp_repo, registry, docker),
        save_credential=SaveCredentialUseCase(mcp_repo, credential_repo, secret, registry),
        validate_credentials=ValidateCredentialsUseCase(
            mcp_repo, credential_repo, secret, registry
        ),
        logs=GetMCPLogsUseCase(mcp_repo, docker),
        metrics=GetMCPMetricsUseCase(mcp_repo, docker),
        connect_cursor=ConnectCursorUseCase(
            mcp_repo, credential_repo, integration_repo, integration, secret, registry
        ),
        local_connection=GetLocalConnectionInfoUseCase(mcp_repo, credential_repo),
        dashboard=GetDashboardStatsUseCase(mcp_repo),
        docker=DockerSDKService(settings.docker_host),
    )


async def get_use_cases() -> UseCaseContainer:
    async with async_session_factory() as session:
        yield build_container(session)
