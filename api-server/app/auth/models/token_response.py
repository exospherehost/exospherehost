from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token for the user")