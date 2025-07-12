import os
import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

from ..models.token_request import TokenRequest
from ..models.token_response import TokenResponse
from ..models.token_claims import TokenClaims

from ..services.session_manager import create_session
from ..services.token_manager import create_token_for_session
from ..services.token_manager import get_active_tokens_for_session

from app.singletons.logs_manager import LogsManager
from app.user.models.user_database_model import User


logger = LogsManager().get_logger()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set or is empty.")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = 3600 # 1 hour


async def create_token(request: TokenRequest, x_exosphere_request_id: str)-> TokenResponse:
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

        # Create token claims
        # Create JWT token
        token_claims = TokenClaims(
            user_id=str(user.id),
            user_name=user.name,
            user_type=user.type,
            verification_status=user.verification_status,
            status=user.status,
            exp=int((datetime.now() + timedelta(seconds=JWT_EXPIRES_IN)).timestamp())
        )

        jwt_token = jwt.encode(token_claims.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Create session first
        session = await create_session(
            token=jwt_token,
            user_id=str(user.id),
            x_exosphere_request_id=x_exosphere_request_id
        )

        if not session:
            logger.error("Session creation failed", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=500, content={"success": False, "detail": "Session creation failed"})


        logger.info(f"Attempting to create session for user {user.id}",
                    x_exosphere_request_id=x_exosphere_request_id)

        # Store token in database with status tracking
        token_doc = await create_token_for_session(
            session_id=str(session.id),
            user_id=str(user.id),
            token=jwt_token
        )

        logger.info("Token successfully created and stored", x_exosphere_request_id=x_exosphere_request_id)

        return TokenResponse(access_token=jwt_token)
    except Exception as e:
        logger.error("Error creating token", error=e, x_exosphere_request_id=x_exosphere_request_id)
        raise e