import os
import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

from ..models.token_request import TokenRequest
from ..models.token_response import TokenResponse
from ..models.token_claims import TokenClaims

from app.singletons.logs_manager import LogsManager

from app.user.models.user_database_model import User

logger = LogsManager().get_logger()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set or is empty.")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = 3600 # 1 hour


async def create_token(request: TokenRequest, x_exosphere_request_id: str) -> TokenResponse:

    try:
        logger.info("Finding user", x_exosphere_request_id=x_exosphere_request_id)

        user = await User.find_one(User.identifier == request.identifier)

        if not user:
            logger.error("User not found", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=404, content={"success": False, "detail": "User not found"})

        if not user.verify_credential(request.credential):
            logger.error("Invalid credential", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=401, content={"success": False, "detail": "Invalid credential"})
        
        logger.info("User found and credential verified", x_exosphere_request_id=x_exosphere_request_id)

        logger.info("User is a super admin", x_exosphere_request_id=x_exosphere_request_id)
        
        token_claims = TokenClaims(
            user_id=str(user.id),
            user_name=user.name,
            user_type=user.type,
            verification_status=user.verification_status,
            status=user.status,
            exp=int((datetime.now() + timedelta(seconds=JWT_EXPIRES_IN)).timestamp())
        )

        return TokenResponse(
            access_token=jwt.encode(token_claims.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        )
    
    except Exception as e:
        logger.error("Error creating token", error=e, x_exosphere_request_id=x_exosphere_request_id)
        raise e