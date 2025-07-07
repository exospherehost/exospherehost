from pydantic import BaseModel

class TokenClaims(BaseModel):
    user_id: str
    user_name: str
    user_type: str
    verification_status: str
    status: str
    exp: int