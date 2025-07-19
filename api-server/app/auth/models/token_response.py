from pydantic import BaseModel, Field
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token for the user")
    refresh_token: Optional[str] = Field(None, description="Refresh token for the user")