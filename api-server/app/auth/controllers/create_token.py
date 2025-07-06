import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

from ..models.token_request import TokenRequest
from ..models.token_response import TokenResponse

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

        print(request.identifier)
        print(request.credential)
        user = await User.objects.get(identifier=request.identifier)
        print(user)
        if not user:
            logger.error("User not found", x_exosphere_request_id=x_exosphere_request_id)
            raise HTTPException(status_code=404, detail="User not found")

        if not user.verify_credential(request.credential):
            logger.error("Invalid credential", x_exosphere_request_id=x_exosphere_request_id)
            raise HTTPException(status_code=401, detail="Invalid credential")
        
        logger.info("User found and credential verified", x_exosphere_request_id=x_exosphere_request_id)

        logger.info("User is a super admin", x_exosphere_request_id=x_exosphere_request_id)
        
        token_claims = {
            "user_id": user.id,
            "user_type": user.type,
            "verification_status": user.verification_status,
            "status": user.status,
            "exp": datetime.now() + timedelta(seconds=JWT_EXPIRES_IN)
        }

        return TokenResponse(
            access_token=jwt.encode(token_claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        )
    
    except Exception as e:
        print(e.message)
        logger.error("Error creating token", error=e, x_exosphere_request_id=x_exosphere_request_id)

        raise HTTPException(status_code=500, detail=str(e))