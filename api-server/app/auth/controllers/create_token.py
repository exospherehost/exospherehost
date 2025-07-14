import os
import jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from bson import ObjectId

from ..models.token_request import TokenRequest
from ..models.token_response import TokenResponse
from ..models.token_claims import TokenClaims

from app.singletons.logs_manager import LogsManager

from app.user.models.user_database_model import User
from app.project.models.project_database_model import Project


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

        previlage = None

        if request.project:

            project = await Project.get(ObjectId(request.project))

            if not project:
                logger.error("Project not found", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=404, content={"success": False, "detail": "Project not found"})
            
            logger.info("Project found", x_exosphere_request_id=x_exosphere_request_id)

            if project.super_admin.ref.id == user.id:
                previlage = "super_admin"

            for user in project.users:
                if user.user.ref.id == user.id:
                    previlage = user.permission.value
                    break

            if not previlage:
                logger.error("User does not have access to the project", x_exosphere_request_id=x_exosphere_request_id)
                return JSONResponse(status_code=403, content={"success": False, "detail": "User does not have access to the project"})
    

        token_claims = TokenClaims(
            user_id=str(user.id),
            user_name=user.name,
            user_type=user.type,
            verification_status=user.verification_status,
            status=user.status,
            project=request.project,
            previlage=previlage,
            satellites=request.satellites,
            exp=int((datetime.now() + timedelta(seconds=JWT_EXPIRES_IN)).timestamp())
        )


        return TokenResponse(
            access_token=jwt.encode(token_claims.model_dump(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        )
    
    except Exception as e:
        logger.error("Error creating token", error=e, x_exosphere_request_id=x_exosphere_request_id)
        raise e