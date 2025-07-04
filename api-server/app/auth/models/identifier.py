from pydantic import BaseModel, Field, model_validator
from .enums import IdentifierType, IdentifierStatus
from ..validators import email_validator, secret_validator

class IdentifierPublic(BaseModel):
    type: IdentifierType = Field(..., description="The type of the identifier")
    value: str = Field(..., description="The value of the identifier")

    @model_validator(mode="after")
    def validate_value(self):
        if self.type == IdentifierType.EMAIL:
            email_validator(self.value)
        elif self.type == IdentifierType.SECRET:
            secret_validator(self.value)
        else:
            raise ValueError("Invalid identifier type")
        return self

class Identifier(IdentifierPublic):
    status: IdentifierStatus = Field(default=IdentifierStatus.NOT_VERIFIED, description="The status of the identifier, managed by system")