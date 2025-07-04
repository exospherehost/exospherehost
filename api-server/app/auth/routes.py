from fastapi import APIRouter, status, Request

from .controllers.auth_user_crud import create_auth_user
from .models.auth_user_create import AuthUserCreateRequest, AuthUserCreateResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/user/register",
    response_model=AuthUserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="The auth user was created successfully",
)
async def create_auth_user_route(body: AuthUserCreateRequest, request: Request):
    x_exosphere_request_id = getattr(request.state, 'x_exosphere_request_id', None)
    return await create_auth_user(body, x_exosphere_request_id)
