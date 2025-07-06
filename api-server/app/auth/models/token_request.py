from pydantic import BaseModel, Field

class TokenRequest(BaseModel):
    identifier: str = Field(..., description="Identifier of the user, could be an email, phone, username, etc.")
    credential: str = Field(..., description="Credential of the user, could be a password, api secret, etc.")