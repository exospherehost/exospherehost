from pydantic import BaseModel, Field
from .user_type_enum import UserTypeEnum
from .verification_status_enum import VerificationStatusEnum
from .user_status_enum import UserStatusEnum
from datetime import datetime


class CreateUserResponse(BaseModel):

    id: str = Field(..., description="Unique identifier for the user")

    name: str = Field(..., description="Human readable name of the user (could be an API user also)")

    type: UserTypeEnum = Field(..., description="Type of the user, human, api, etc. (enum)")

    identifier: str = Field(..., description="Unique identifier for the user, could be an email, phone, username, etc.")

    verification_status: VerificationStatusEnum = Field(..., description="Verification status of the user, verified, not_verified, blocked, deleted, not_required (enum)")

    status: UserStatusEnum = Field(..., description="Status of the user, active, inactive, deleted, blocked (enum)")

    created_at: datetime = Field(..., description="Date and time when the user was created")

    updated_at: datetime = Field(..., description="Date and time when the user was last updated")