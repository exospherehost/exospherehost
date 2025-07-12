from beanie import Document, Indexed, before_event, Replace, Save
from datetime import datetime, timedelta
from .token_status_enum import TokenStatusEnum
from pydantic import Field
from typing import Optional



class Token(Document):
    session_id: str = Field(..., description="Unique identifier for the session associated with the token")
    user_id: str = Field(..., description="Unique identifier for the user associated with the token")
    token: str  # Store hashed version for security
    status: TokenStatusEnum = Field(default=TokenStatusEnum.ACTIVE, description="Status of the token")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date and time when the token was created")
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24), description="Date and time when the token expires")
    last_used_at: Optional[datetime] = None

    class Settings:
        name = "tokens"
        indexes = [
            [("user_id", 1), ("status", 1)],
            [("session_id", 1), ("status", 1)],
            [("token_hash", 1)],
            [("expires_at", 1)],  # Essential for cleanup operations
        ]