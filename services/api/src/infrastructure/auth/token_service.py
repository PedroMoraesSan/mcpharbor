import hashlib
import secrets

from domain.services.auth_service import AgentContext, AuthService
from infrastructure.persistence.database import async_session_factory
from infrastructure.persistence.repositories import SQLAlchemyAgentRepository


def generate_token() -> tuple[str, str]:
    raw = f"harbour_sk_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class TokenAuthService(AuthService):
    def __init__(self) -> None:
        self._session_factory = async_session_factory

    async def authenticate(self, token: str) -> AgentContext | None:
        hashed = hash_token(token)
        async with self._session_factory() as session:
            repo = SQLAlchemyAgentRepository(session)
            agent = await repo.get_by_token_hash(hashed)
            if not agent:
                return None
            return AgentContext(agent_id=str(agent.id), agent_name=agent.name)
