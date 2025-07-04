import bcrypt
from pydantic import BaseModel, Field
from .enums import AuthMethods
from datetime import datetime


class Credential(BaseModel):
    method: AuthMethods = Field(..., description="The method of the credential")
    key: str = Field(..., description="The key of the credential")
    name: str = Field(default="", description="The name of the credential")
    created_at: datetime = Field(default_factory=datetime.now, description="The date and time the credential was created, optional system generated")

    @staticmethod
    def generate_hash(method: AuthMethods, key: str, name: str = "") -> "Credential":
        hashed = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()
        return Credential(method=method, key=hashed, name=name)

    def verify_hash(self, key: str) -> bool:
        return bcrypt.checkpw(key.encode(), self.key.encode())

