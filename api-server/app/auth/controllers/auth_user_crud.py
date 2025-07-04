from fastapi import HTTPException
from fastapi.responses import JSONResponse

from ..models.auth_user_database import AuthUser
from ..models.auth_user_create import AuthUserCreateRequest, AuthUserCreateResponse
from ..models.identifier import Identifier
from ..models.credential import Credential

from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


async def create_auth_user(request: AuthUserCreateRequest, x_exosphere_request_id: str) -> AuthUserCreateResponse:
    try:
        auth_user = AuthUser(
            name=request.name,
            identifiers=[
                Identifier(type=identifier.type, value=identifier.value)
                for identifier in request.identifiers
            ],
            credentials=[
                Credential.generate_hash(
                    method=credential.method, key=credential.key, name=credential.name
                )
                for credential in request.credentials
            ],
        )
        await auth_user.insert()
        return AuthUserCreateResponse(
            id=str(auth_user.id), name=auth_user.name, identifiers=auth_user.identifiers
        )
    except Exception as e:
        logger.error(
            "error creating auth user",
            error=str(e),
            x_exosphere_request_id=x_exosphere_request_id,
        )
        if "E11000" in str(e):
            return JSONResponse(
                status_code=400, content={"message": "User already exists"}
            )
        raise HTTPException(status_code=500, detail=str(e))
