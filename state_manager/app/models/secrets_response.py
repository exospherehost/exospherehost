from pydantic import BaseModel, Field
from typing import Dict


class SecretsResponseModel(BaseModel):
    secrets: Dict[str, str] = Field(..., description="Dictionary of secret names to their values") 