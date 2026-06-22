from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from application.use_cases.install_mcp import InstallMCPUseCase
from application.use_cases.start_mcp import StartMCPUseCase
from application.use_cases.stop_mcp import StopMCPUseCase
from application.use_cases.uninstall_mcp import UninstallMCPUseCase
from domain.entities.catalog import CredentialField, MCPCatalogEntry
from domain.entities.credential import Credential
from domain.entities.mcp import MCP
from domain.value_objects.enums import MCPStatus
from infrastructure.integration.cursor_service import CursorIntegrationService
from infrastructure.mcp.gateway import GatewaySession
from shared.result import Failure, Success


@pytest.mark.asyncio
async def test_install_mcp_success():
    registry = AsyncMock()
    mcp_repo = AsyncMock()
    docker = AsyncMock()

    entry = MCPCatalogEntry(
        id="github",
        name="GitHub MCP",
        description="test",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
        credentials=[CredentialField(key="GITHUB_PERSONAL_ACCESS_TOKEN", label="PAT")],
    )
    registry.get_by_id.return_value = entry
    mcp_repo.get_by_catalog_id.return_value = None
    mcp_repo.save.side_effect = lambda m: m

    use_case = InstallMCPUseCase(registry, mcp_repo, docker)
    result = await use_case.execute("github")

    assert isinstance(result, Success)
    assert result.value.catalog_id == "github"


@pytest.mark.asyncio
async def test_install_mcp_duplicate():
    registry = AsyncMock()
    mcp_repo = AsyncMock()
    docker = AsyncMock()

    existing = MCP(
        id=uuid4(),
        catalog_id="github",
        name="GitHub MCP",
        description="",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
    )
    registry.get_by_id.return_value = MCPCatalogEntry(
        id="github",
        name="GitHub MCP",
        description="",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
    )
    mcp_repo.get_by_catalog_id.return_value = existing

    use_case = InstallMCPUseCase(registry, mcp_repo, docker)
    result = await use_case.execute("github")

    assert isinstance(result, Failure)
    assert result.code == "duplicate"


@pytest.mark.asyncio
async def test_uninstall_mcp_success():
    mcp_id = uuid4()
    mcp = MCP(
        id=mcp_id,
        catalog_id="github",
        name="GitHub MCP",
        description="",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
        status=MCPStatus.STOPPED,
        container_id="abc123",
    )

    mcp_repo = AsyncMock()
    credential_repo = AsyncMock()
    integration_repo = AsyncMock()
    integration_service = AsyncMock()
    docker = AsyncMock()
    secret = AsyncMock()

    mcp_repo.get_by_id.return_value = mcp
    credential_repo.get_by_mcp_id.return_value = [
        Credential(
            id=uuid4(),
            mcp_id=mcp_id,
            key_name="GITHUB_PERSONAL_ACCESS_TOKEN",
            keyring_ref=f"{mcp_id}:GITHUB_PERSONAL_ACCESS_TOKEN",
        )
    ]

    use_case = UninstallMCPUseCase(
        mcp_repo, credential_repo, integration_repo, integration_service, docker, secret
    )
    result = await use_case.execute(mcp_id)

    assert isinstance(result, Success)
    assert result.value["catalog_id"] == "github"
    docker.stop_container.assert_called_once_with("abc123")
    docker.remove_container.assert_called_once_with("abc123")
    secret.delete.assert_called_once()
    credential_repo.delete_by_mcp_id.assert_called_once_with(mcp_id)
    integration_service.disconnect_cursor.assert_called_once_with(mcp)
    integration_repo.delete_by_mcp_id.assert_called_once_with(mcp_id)
    mcp_repo.delete.assert_called_once_with(mcp_id)


@pytest.mark.asyncio
async def test_uninstall_mcp_not_found():
    mcp_repo = AsyncMock()
    mcp_repo.get_by_id.return_value = None

    use_case = UninstallMCPUseCase(
        mcp_repo, AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()
    )
    result = await use_case.execute(uuid4())

    assert isinstance(result, Failure)
    assert result.code == "not_found"


@pytest.mark.asyncio
@patch("application.use_cases.start_mcp.gateway_manager")
async def test_start_mcp_success(mock_gateway):
    mcp_id = uuid4()
    mcp = MCP(
        id=mcp_id,
        catalog_id="github",
        name="GitHub MCP",
        description="",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
        status=MCPStatus.STOPPED,
    )

    mcp_repo = AsyncMock()
    credential_repo = AsyncMock()
    secret = AsyncMock()
    registry = AsyncMock()
    integration = AsyncMock(spec=CursorIntegrationService)

    mcp_repo.get_by_id.return_value = mcp
    mcp_repo.save.side_effect = lambda m: m
    registry.get_by_id.return_value = MCPCatalogEntry(
        id="github",
        name="GitHub MCP",
        description="",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
        credentials=[CredentialField(key="GITHUB_PERSONAL_ACCESS_TOKEN", label="PAT")],
    )
    credential_repo.get_by_mcp_id.return_value = [
        Credential(
            id=uuid4(),
            mcp_id=mcp_id,
            key_name="GITHUB_PERSONAL_ACCESS_TOKEN",
            keyring_ref=f"{mcp_id}:GITHUB_PERSONAL_ACCESS_TOKEN",
        )
    ]
    secret.get.return_value = "ghp_test_token"
    mock_gateway.get.return_value = None
    mock_gateway.start = AsyncMock(
        return_value=GatewaySession(
            mcp_id=mcp_id,
            port=18042,
            _task=MagicMock(done=MagicMock(return_value=False)),
        )
    )
    docker = AsyncMock()
    docker.ensure_image = AsyncMock()

    use_case = StartMCPUseCase(mcp_repo, credential_repo, secret, registry, integration, docker)
    result = await use_case.execute(mcp_id)

    assert isinstance(result, Success)
    assert result.value.status == MCPStatus.RUNNING.value
    assert result.value.local_endpoint == "http://127.0.0.1:18042/mcp"
    mock_gateway.start.assert_called_once()
    integration.install_wrapper.assert_called_once()


@pytest.mark.asyncio
@patch("application.use_cases.start_mcp.gateway_manager")
async def test_start_mcp_without_required_credentials(mock_gateway):
    mcp_id = uuid4()
    mcp = MCP(
        id=mcp_id,
        catalog_id="docker",
        name="Docker MCP",
        description="",
        author="Docker",
        version="latest",
        docker_image="mcp/docker",
        status=MCPStatus.STOPPED,
    )

    mcp_repo = AsyncMock()
    credential_repo = AsyncMock()
    secret = AsyncMock()
    registry = AsyncMock()
    integration = AsyncMock(spec=CursorIntegrationService)

    mcp_repo.get_by_id.return_value = mcp
    mcp_repo.save.side_effect = lambda m: m
    registry.get_by_id.return_value = MCPCatalogEntry(
        id="docker",
        name="Docker MCP",
        description="",
        author="Docker",
        version="latest",
        docker_image="mcp/docker",
        credentials=[],
    )
    credential_repo.get_by_mcp_id.return_value = []
    mock_gateway.get.return_value = None
    mock_gateway.start = AsyncMock(
        return_value=GatewaySession(
            mcp_id=mcp_id,
            port=18043,
            _task=MagicMock(done=MagicMock(return_value=False)),
        )
    )
    docker = AsyncMock()
    docker.ensure_image = AsyncMock()

    use_case = StartMCPUseCase(mcp_repo, credential_repo, secret, registry, integration, docker)
    result = await use_case.execute(mcp_id)

    assert isinstance(result, Success)
    mock_gateway.start.assert_called_once()


@pytest.mark.asyncio
@patch("application.use_cases.stop_mcp.gateway_manager")
async def test_stop_mcp_success(mock_gateway):
    mcp_id = uuid4()
    mcp = MCP(
        id=mcp_id,
        catalog_id="github",
        name="GitHub MCP",
        description="",
        author="GitHub",
        version="latest",
        docker_image="ghcr.io/github/github-mcp-server",
        status=MCPStatus.RUNNING,
        container_id="18042",
        container_name="gateway-18042",
    )

    mcp_repo = AsyncMock()
    credential_repo = AsyncMock()
    mcp_repo.get_by_id.return_value = mcp
    mcp_repo.save.side_effect = lambda m: m
    credential_repo.get_by_mcp_id.return_value = []
    mock_gateway.stop = AsyncMock()

    use_case = StopMCPUseCase(mcp_repo, credential_repo)
    result = await use_case.execute(mcp_id)

    assert isinstance(result, Success)
    assert result.value.status == MCPStatus.STOPPED.value
    mock_gateway.stop.assert_called_once_with(mcp_id)
