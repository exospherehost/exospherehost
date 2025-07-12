from datetime import datetime, UTC
from beanie import Document, Indexed, before_event, Replace, Save
from pydantic import Field
from .session_status_enum import SessionStatusEnum
from .token_status_enum import TokenStatusEnum

class Session(Document):
    user_id: str = Field(..., description="Unique identifier for the user associated with the session")
    created_at: datetime = Field(default_factory=datetime.now, description="Date and time when the session was created")
    expires_at: datetime = Field(..., description="Date and time when the session expires")
    last_activity: datetime = Field(default_factory=datetime.now, description="Date and time of the last activity in the session")
    session_status: SessionStatusEnum = Field(default=SessionStatusEnum.ACTIVE, description="Status of the session, active, inactive (enum)")

    @staticmethod
    def create_new_session(user_id: str, expires_at: datetime) -> "Session":
        session = Session(
            user_id=user_id,
            expires_at=expires_at,
            session_status=SessionStatusEnum.ACTIVE,
        )
        return session

    @before_event([Save, Replace])
    def update_last_activity(self):
        self.last_activity = datetime.now()