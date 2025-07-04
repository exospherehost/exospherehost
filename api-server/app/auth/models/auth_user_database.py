from beanie import Document, before_event, Replace, Save
from pydantic import Field, model_validator
from typing import List
from datetime import datetime
from pymongo import IndexModel, ASCENDING
from .identifier import Identifier
from .enums import UserStatus
from .credential import Credential


class AuthUser(Document):
    name: str = Field(..., description="The name of the user", pattern=r"^[a-zA-Z0-9_]+$")
    identifiers: List[Identifier] = Field(
        ..., description="The identifiers of the user"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="The date and time the user was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="The date and time the user was updated",
    )
    status: UserStatus = Field(
        default=UserStatus.ACTIVE, description="The status of the user"
    )
    credentials: List[Credential] = Field(
        default_factory=list, description="The credentials of the user"
    )


    @before_event(Replace, Save)
    def update_updated_at(self):
        self.updated_at = datetime.now()

    @model_validator(mode="after")
    def validate_indentifiers_unique(self):
        if len(self.identifiers) != len(
            set(identifier.value for identifier in self.identifiers)
        ):
            raise ValueError("Identifiers must be unique!")
        return self
    
    @model_validator(mode="after")
    def validate_credentials_unique(self):
        if len(self.credentials) != len(
            set(credential.method for credential in self.credentials)
        ):
            raise ValueError("Credentials must be unique!")
        return self

    class Settings:
        name = "auth_user"

        indexes = [
            IndexModel(
                [("identifiers.value", ASCENDING)],
                unique=True,
                sparse=True,
                name="identifiers_value",
            )
        ]
