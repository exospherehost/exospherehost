from pydantic import BaseModel, Field
from .user_type_enum import UserTypeEnum

class CreateUserRequest(BaseModel):

    name: str = Field(..., description="Human readable name of the user (could be an API user also)")

    type: UserTypeEnum = Field(..., description="Type of the user, human, api, etc. (enum)")

    identifier: str = Field(..., description="Unique identifier for the user, could be an email, phone, username, etc.")

    credential: str = Field(..., description="Credential of the user, stores hashed password, Api secret, etc.")
