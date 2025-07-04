from pydantic import BaseModel, Field, model_validator
from typing import List
from .identifier import IdentifierPublic
from .credential import Credential


class AuthUserCreateRequest(BaseModel):
    name: str = Field(...)
    identifiers: List[IdentifierPublic]
    credentials: List[Credential]

    @model_validator(mode="after")
    def validate_identifiers_unique(self):
        if len(self.identifiers) == 0:
            raise ValueError("At least one identifier is required!")
        return self

    @model_validator(mode="after")
    def validate_credentials_unique(self):
        if len(self.credentials) == 0:
            raise ValueError("At least one credential is required!")
        return self


class AuthUserCreateResponse(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    identifiers: List[IdentifierPublic]
