import os
import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from bson import ObjectId
from typing import Union
from ..models.refresh_token_request import RefreshTokenRequest
from ..models.token_response import TokenResponse
from ..models.token_claims import TokenClaims
from ..models.token_type_enum import TokenType

from app.singletons.logs_manager import LogsManager

from app.user.models.user_database_model import User
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum
from app.project.models.project_database_model import Project

logger = LogsManager().get_logger()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set or is empty.")

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = 3600  # 1 hour

async def refresh_access_token(
    request: RefreshTokenRequest, 
    x_exosphere_request_id: str
) -> "Union[TokenResponse,JSONResponse]":
    """
    Takes refresh token and returns a new access token.
    Denies for inactive/blocked or unverified users.
    Returns errors as JSONResponse, not raw exceptions.
    """
    try:
        # Decode refresh token
        payload = jwt.decode(
            request.refresh_token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]
        )
        
        # Verify it's a refresh token
        if payload.get("token_type") != TokenType.refresh.value:
            return JSONResponse(
                status_code=401, 
                content={"detail": "Invalid token type"}
            )

        # Get user
        user = await User.get(ObjectId(payload["user_id"]))
        if not user:
            return JSONResponse(
                status_code=401,
                content={"detail": "User not found"}
            )
        
         # Define a list of statuses for which token refresh is not allowed
        DISALLOWED_STATUSES = [
            UserStatusEnum.INACTIVE.value,
            UserStatusEnum.BLOCKED.value
        ]

        # Deny if user status is in the disallowed list
        if user.status in DISALLOWED_STATUSES:
            logger.warning(
                f"User with disallowed status attempted token refresh: {user.id} (status: {user.status})",
                x_exosphere_request_id=x_exosphere_request_id
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "TOKEN NOT ALLOWED: User account is inactive or blocked."}
            )
        
        # Deny if unverified
        if user.verification_status == VerificationStatusEnum.NOT_VERIFIED.value:
            logger.error(
                "Unverified user - refresh token request denied", 
                x_exosphere_request_id=x_exosphere_request_id
            )
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "User is not verified"}
            )


        privilege = None
        project_id = payload.get("project")
        if project_id:
            project = await Project.get(ObjectId(project_id))
            if not project:
                logger.error("Project not found", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=404, content={"success": False, "detail": "Project not found"})
            logger.info("Project found", x_exosphere_request_id=x_exosphere_request_id)
            if project.super_admin.ref.id == user.id:
                privilege = "super_admin"
            for project_user in project.users:
                if project_user.user.ref.id == user.id:
                    privilege = project_user.permission.value
                    break
            if not privilege:
                logger.error("User does not have access to the project", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=403, content={"success": False, "detail": "User does not have access to the project"})

        # Create new access token
        token_claims = TokenClaims(
            user_id=str(user.id),
            user_name=user.name,
            user_type=user.type,
            verification_status=user.verification_status,
            status=user.status,
            project=project_id,  
            previlage=privilege,  
            satellites=payload.get("satellites"),
            exp=int((datetime.now() + timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
            token_type=TokenType.access.value
        )
        
        new_access_token = jwt.encode(
            token_claims.model_dump(), 
            JWT_SECRET_KEY, 
            algorithm=JWT_ALGORITHM
        )
        # Return ONLY new access token (not a new refresh token)
        return TokenResponse(
            access_token=new_access_token
        )
        
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Refresh token expired"}
        )
    except Exception as e:
        logger.error(
            "Error refreshing token", 
            error=e, 
            x_exosphere_request_id=x_exosphere_request_id
        )
        # Always return JSONResponse for errors so your tests pass
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": "Internal server error"}
        )
