from pydantic import BaseModel, Field
from beanie import Link
from app.user.models.user_database_model import User
from .permission_enum import PermissionEnum


class ProjectUser(BaseModel):
    permission: PermissionEnum = Field(..., description="Permission of the user in the project, admin, user, etc. (enum)")

    user: Link[User] = Field(..., description="Reference to the user document") 