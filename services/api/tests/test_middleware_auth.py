from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.auth.token_service import generate_token
from infrastructure.persistence.models import AgentModel
from main import create_app


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

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()


@pytest.mark.asyncio
async def test_health_is_public(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_admin_routes_are_public(client):
    resp = await client.get("/api/v1/mcps")
    assert resp.status_code == 200

    resp = await client.get("/api/v1/catalog")
    assert resp.status_code == 200

    resp = await client.post("/api/v1/agents", json={"name": "test-agent"})
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_protected_route_returns_401_without_token(client):
    resp = await client.get("/api/v1/mcp")
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "unauthorized"


@pytest.mark.asyncio
async def test_protected_route_returns_401_with_invalid_token(client):
    resp = await client.get(
        "/api/v1/mcp",
        headers={"Authorization": "Bearer invalid_token_123"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "unauthorized"


@pytest.mark.asyncio
async def test_protected_route_with_malformed_auth_header(client):
    resp = await client.get(
        "/api/v1/mcp",
        headers={"Authorization": "NotBearer something"},
    )
    assert resp.status_code == 401

    resp = await client.get(
        "/api/v1/mcp",
        headers={"Authorization": ""},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_passes_middleware_with_valid_token(test_database_url):
    raw_token, token_hash = generate_token()
    agent_id = uuid4()

    engine = create_async_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        session.add(AgentModel(id=agent_id, name="auth-test-agent", token_hash=token_hash))
        await session.commit()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(
            "/api/v1/mcp",
            headers={"Authorization": f"Bearer {raw_token}"},
        )

    assert resp.status_code == 404

    await engine.dispose()
