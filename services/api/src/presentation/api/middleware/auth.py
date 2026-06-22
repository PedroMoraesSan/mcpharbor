from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from infrastructure.auth.token_service import TokenAuthService

AUTH_REQUIRED_EXACT = {"/api/v1/mcp"}


def _requires_auth(path: str) -> bool:
    if path in AUTH_REQUIRED_EXACT:
        return True
    return any(path.startswith(p + "/") for p in AUTH_REQUIRED_EXACT)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._auth_service = TokenAuthService()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if _requires_auth(path):
            auth = request.headers.get("Authorization", "")
            token = auth.removeprefix("Bearer ").strip()
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": {
                            "error": "Missing authorization token",
                            "code": "unauthorized",
                        }
                    },
                )

            agent = await self._auth_service.authenticate(token)
            if not agent:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": {
                            "error": "Invalid token",
                            "code": "unauthorized",
                        }
                    },
                )

            request.state.agent = agent

        return await call_next(request)
