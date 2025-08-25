from typing import Union
import os
import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from bson import ObjectId
from bson.errors import InvalidId

from ..models.token_request import TokenRequest
from ..models.token_response import TokenResponse
from ..models.token_claims import TokenClaims
from ..models.token_type_enum import TokenType

from app.singletons.logs_manager import LogsManager
from app.user.models.user_database_model import User
from app.project.models.project_database_model import Project
from app.auth.constants import DENIED_USER_STATUSES

logger = LogsManager().get_logger()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set or is empty")

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = 3600        # 1 hour
REFRESH_EXPIRES_IN = 3600*24 # 1 day


async def create_token(request: TokenRequest, x_exosphere_request_id: str) -> Union[JSONResponse, TokenResponse]:
    try:
        logger.info("Finding user", x_exosphere_request_id=x_exosphere_request_id)
        user = await User.find_one(User.identifier == request.identifier)

        if not user:
            logger.error("User not found", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=404, content={"success": False, "detail": "User not found"})

        if not user.verify_credential(request.credential):
            logger.error("Invalid credential", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=401, content={"success": False, "detail": "Invalid credential"})
        
        # Deny users with statuses in DENIED_USER_STATUSES
        status = getattr(user, "status", None)
        status_value = getattr(status, "value", status)
        if status_value in DENIED_USER_STATUSES:
            logger.error("Inactive or blocked user - token request denied", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=403, content={"success": False, "detail": "User is inactive or blocked"})

        logger.info("User found and credential verified", x_exosphere_request_id=x_exosphere_request_id)

        # Deny unverified users
        verification_status = getattr(user, "verification_status", None)
        verification_status_value = getattr(verification_status, "value", verification_status)
        if verification_status_value in {"NOT_VERIFIED", "BLOCKED", "DELETED"}:
            logger.error("Unverified user - token request denied", x_exosphere_request_id=x_exosphere_request_id)
            return JSONResponse(status_code=403, content={"success": False, "detail": "User is not verified"})

        previlage = None
        if request.project:
            try:
                project = await Project.get(ObjectId(request.project))
            except InvalidId:
                logger.error("Invalid project id", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=400, content={"success": False, "detail": "Invalid project id"})
            except Exception as e:
                logger.error("Error loading project", error=e, x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=500, content={"success": False, "detail": "Internal server error"})
            if not project:
                logger.error("Project not found", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=404, content={"success": False, "detail": "Project not found"})
            logger.info("Project found", x_exosphere_request_id=x_exosphere_request_id)
            if project.super_admin.ref.id == user.id:
                previlage = "super_admin"
            else:    
                for project_user in project.users:
                    if project_user.user.ref.id == user.id:
                        previlage = project_user.permission.value
                        break
            if not previlage:
                logger.error("User does not have access to the project", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=403, content={"success": False, "detail": "User does not have access to the project"})
        

        # Prepare claims
        token_claims = TokenClaims(
            user_id=str(user.id),
            user_name=user.name,
            user_type=user.type,
            verification_status=verification_status_value,
            status=status_value,
            project=request.project,
            previlage=previlage,
            satellites=request.satellites,
            exp=int((datetime.now() + timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
            token_type=TokenType.access.value
        )
        refresh_claims = TokenClaims(
            user_id=str(user.id),
            user_name=user.name,
            user_type=user.type,
            verification_status=verification_status_value,
            status=status_value,
            project=request.project,
            previlage=previlage,
            satellites=request.satellites,
            exp=int((datetime.now() + timedelta(seconds=REFRESH_EXPIRES_IN)).timestamp()),
            token_type=TokenType.refresh.value
        )

        # Return tokens
        return TokenResponse(
            access_token=jwt.encode(token_claims.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
            refresh_token=jwt.encode(refresh_claims.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        )
    except Exception as e:
        logger.error("Error creating token", error=e, x_exosphere_request_id=x_exosphere_request_id)
        return JSONResponse(status_code=500, content={"success": False, "detail": "Internal server error"})