from fastapi import APIRouter, status, Request

from .controllers.create_user import create_user
from .models.create_user_request import CreateUserRequest
from .models.create_user_response import CreateUserResponse
 
router = APIRouter(prefix="/v0/user", tags=["user"])

@router.post(
    "/",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="User created successfully"
)
async def create_user_route(body: CreateUserRequest, request: Request):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    return await create_user(body, x_exosphere_request_id)