from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import create_app
from presentation.api.dependencies import build_container, get_use_cases


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client(test_database_url):
    engine = create_async_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_use_cases():
        async with session_factory() as session:
            yield build_container(session)

    app = create_app()
    app.dependency_overrides[get_use_cases] = override_get_use_cases

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_catalog(client):
    response = await client.get("/api/v1/catalog")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == "github"


@pytest.mark.asyncio
async def test_list_mcps_empty(client):
    response = await client.get("/api/v1/mcps")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_uninstall_mcp_not_found(client):
    response = await client.delete(f"/api/v1/mcps/{uuid4()}")
    assert response.status_code == 404
