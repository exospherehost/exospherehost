from ..models.create_project_request import CreateProjectRequest
from ..models.create_project_response import CreateProjectResponse
from ..models.project_database_model import Project

from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


async def create_project(request: CreateProjectRequest, x_exosphere_request_id: str) -> CreateProjectResponse:
    try:
        logger.info("Creating new project", x_exosphere_request_id=x_exosphere_request_id)
        project = Project(
            name=request.name
        )
        await project.save()
        return CreateProjectResponse(**project.model_dump())
    
    except Exception as e:
        logger.error("Error creating new project", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e