from fastapi import Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader 
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config.settings import get_settings

API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def check_api_key(api_key_header: str = Depends(api_key_header)):
    settings = get_settings()
    if api_key_header == settings.state_manager_secret:
        return api_key_header
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    