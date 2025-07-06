from fastapi import APIRouter, status, Request

from .controllers.create_token import create_token
from .models.token_request import TokenRequest
from .models.token_response import TokenResponse

router = APIRouter(prefix="/v0/auth", tags=["auth"])

@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    response_description="Token created successfully"
)
async def create_token_route(body: TokenRequest, request: Request):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    return await create_token(body, x_exosphere_request_id)