import bcrypt, os
from datetime import datetime
from beanie import Document, before_event, Replace, Save
from pydantic import Field
from .user_type_enum import UserTypeEnum
from .verification_status_enum import VerificationStatusEnum
from .user_status_enum import UserStatusEnum


class User(Document):

    name: str = Field(..., description="Human readable name of the user (could be an API user also)")

    type: UserTypeEnum = Field(..., description="Type of the user, human, api, etc. (enum)")

    identifier: str = Field(..., description="Unique identifier for the user, could be an email, phone, username, etc.", unique=True)

    verification_status: VerificationStatusEnum = Field(default=VerificationStatusEnum.NOT_VERIFIED, description="Verification status of the user, verified, not_verified, blocked, deleted, not_required (enum)")

    credential: str = Field(..., description="Credential of the user, stores hashed password, Api secret, etc.")

    status: UserStatusEnum = Field(default=UserStatusEnum.ACTIVE, description="Status of the user, active, inactive, deleted, blocked (enum)")

    created_at: datetime = Field(default_factory=datetime.now, description="Date and time when the user was created")

    updated_at: datetime = Field(default_factory=datetime.now, description="Date and time when the user was last updated")

    @staticmethod
    def create_new_user(name: str, type: UserTypeEnum, identifier: str, credential: str, verification_status: VerificationStatusEnum = VerificationStatusEnum.NOT_VERIFIED, status: UserStatusEnum = UserStatusEnum.ACTIVE) -> "User":
        user = User(
            name=name,
            type=type,
            identifier=identifier,
            credential=bcrypt.hashpw(credential.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            verification_status=verification_status,
            status=status
        )
        return user
    
    def verify_credential(self, credential: str) -> bool:
        return bcrypt.checkpw(credential.encode('utf-8'), self.credential.encode('utf-8'))

    @before_event([Save, Replace])
    def update_updated_at(self):
        self.updated_at = datetime.now()
