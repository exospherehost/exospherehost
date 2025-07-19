from fastapi import APIRouter, status, Request

from .controllers.create_token import create_token
from .controllers.refresh_access_token import refresh_access_token
from .models.token_request import TokenRequest
from .models.token_response import TokenResponse
from .models.refresh_token_request import RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    response_description="Token created successfully"
)
async def create_token_route(body: TokenRequest, request: Request):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    return await create_token(body, x_exosphere_request_id)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    response_description="Access token refreshed successfully"
)
async def refresh_token_route(body: RefreshTokenRequest, request: Request):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    return await refresh_access_token(body, x_exosphere_request_id)