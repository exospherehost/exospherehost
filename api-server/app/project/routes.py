from fastapi import APIRouter, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from starlette.responses import JSONResponse

from .controllers.create_project import create_project
from .models.create_project_request import CreateProjectRequest
from .models.create_project_response import CreateProjectResponse

from app.auth.services.get_token_claims import get_token_claims

router = APIRouter(prefix="/v0/project", tags=["project"])

@router.post(
    "/",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Project created successfully"
)
async def create_project_route(body: CreateProjectRequest, request: Request, token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    claims = await get_token_claims(token.credentials, x_exosphere_request_id)

    if claims is None:
        return JSONResponse(status_code=401, content={"message": "Invalid token", "success": False})

    return await create_project(body, claims, x_exosphere_request_id)