from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class GetAuthUserFromAPIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        auth_user = getattr(request.state, 'auth_user', None)
        x_api_key = request.headers.get("X-API-KEY")
        x_secret_identifier = request.headers.get("X-SECRET-IDENTIFIER")

        if auth_user:
            return await call_next(request)

        if x_api_key and x_secret_identifier:
            auth_user = await get_auth_user_from_api_key(x_api_key, x_secret_identifier)

        return await call_next(request)