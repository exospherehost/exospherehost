from beanie import Link
from bson import ObjectId

from ..models.create_project_request import CreateProjectRequest
from ..models.create_project_response import CreateProjectResponse
from ..models.project_database_model import Project

from app.singletons.logs_manager import LogsManager
from app.auth.models.token_claims import TokenClaims
from app.user.models.user_database_model import User

logger = LogsManager().get_logger()


async def create_project(request: CreateProjectRequest, claims: TokenClaims, x_exosphere_request_id: str) -> CreateProjectResponse:
    try:
        logger.info("Creating new project", x_exosphere_request_id=x_exosphere_request_id, user_id=claims.user_id)
        project = Project(
            name=request.name,
            super_admin=Link(ObjectId(claims.user_id), User)
        )
        await project.save()
        print(project)
        return CreateProjectResponse(
            id=str(project.id),
            name=project.name,
            status=project.status,
            billing_account=project.billing_account,
            super_admin=claims.user_id,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    
    except Exception as e:
        logger.error("Error creating new project", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e