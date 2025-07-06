from fastapi import APIRouter, status, Request

from .controllers.create_project import create_project
from .models.create_project_request import CreateProjectRequest
from .models.create_project_response import CreateProjectResponse

router = APIRouter(prefix="/v0/project", tags=["project"])

@router.post(
    "/",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Project created successfully"
)
async def create_project_route(body: CreateProjectRequest, request: Request):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    return await create_project(body, x_exosphere_request_id)