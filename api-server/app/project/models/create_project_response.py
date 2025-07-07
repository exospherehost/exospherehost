from pydantic import BaseModel
from .project_database_model import Project
from .billing_account import BillingAccount
from .project_user import ProjectUser
from .project_status_enum import ProjectStatusEnum
from beanie import Link
from typing import List
from app.user.models.user_database_model import User
from datetime import datetime


class CreateProjectResponse(BaseModel):
    id: str
    name: str
    status: ProjectStatusEnum
    billing_account: BillingAccount
    super_admin: str
    created_at: datetime
    updated_at: datetime