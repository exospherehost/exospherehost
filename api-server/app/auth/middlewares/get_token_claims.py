import jwt
import os

from starlette.middleware.base import BaseHTTPMiddleware
from app.singletons.logs_manager import LogsManager
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..models.token_claims import TokenClaims

logger = LogsManager().get_logger()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set or is empty.")
JWT_ALGORITHM = "HS256"


class GetTokenClaimsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        token = request.headers.get("Authorization")

        if token:
            if not token.startswith("Bearer "):
                logger.error("Invalid token format", x_exosphere_request_id=getattr(request.state, 'x_exosphere_request_id', None))
                return JSONResponse(status_code=401, content={"message": "Invalid token format", "success": False})
            
            try:
                token_claims = jwt.decode(token.split(" ")[1], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                request.state.token_claims = TokenClaims(**token_claims)
                logger.info("Token claims decoded", x_exosphere_request_id=getattr(request.state, 'x_exosphere_request_id', None), user_id=request.state.token_claims.user_id)

            except Exception as e:
                logger.error("Error decoding token", error=e, x_exosphere_request_id=getattr(request.state, 'x_exosphere_request_id', None))

                return JSONResponse(status_code=401, content={"message": "Invalid token", "success": False})
                
        else:
            logger.error("No token provided", x_exosphere_request_id=getattr(request.state, 'x_exosphere_request_id', None))
            request.state.token_claims = None

        return await call_next(request)