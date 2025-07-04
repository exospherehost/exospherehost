from beanie import Document
from datetime import datetime
from pymongo import IndexModel, ASCENDING


class RevokedToken(Document):
    jti: str
    expires_at: datetime

    class Settings:
        name = "revoked_tokens"
        indexes = [
            IndexModel(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=0,
            ),
        ]

