from fastapi import APIRouter, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from fastapi.responses import JSONResponse

from app.auth.services.get_token_claims import get_token_claims
from .controllers.register_satellite import register_satellite

from .models.register_satellite_request import RegisterSatelliteRequest
from .models.register_satellite_response import RegisterSatelliteResponse

router = APIRouter(prefix="/v0/project/{project_id}/satellite", tags=["satellite"])

@router.post(
    "/",
    response_model=RegisterSatelliteResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Satellite registered successfully"
)
async def register_satellite_route(project_id: str, body: RegisterSatelliteRequest, request: Request, token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", None)
    claims = await get_token_claims(token.credentials, x_exosphere_request_id)

    if claims is None or claims.project != project_id:
        return JSONResponse(status_code=401, content={"message": "Invalid token", "success": False})
    
    return await register_satellite(body, project_id, claims, x_exosphere_request_id)