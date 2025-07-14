from pydantic import BaseModel
from typing import Optional

class TokenClaims(BaseModel):
    user_id: str
    user_name: str
    user_type: str
    verification_status: str
    status: str
    project: Optional[str] = None
    previlage: Optional[str] = None
    satellites: Optional[list[str]] = None
    exp: int