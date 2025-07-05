from datetime import datetime
from beanie import Document, before_event, Replace, Save, Link
from typing import List
from pydantic import Field
from .project_status_enum import ProjectStatusEnum
from .billing_account import BillingAccount
from .project_user import ProjectUser
from app.user.models.user_database_model import User


class Project(Document):

    name: str = Field(..., description="Name of the project (human readable)")

    status: ProjectStatusEnum = Field(default=ProjectStatusEnum.ACTIVE, description="Status of the project (enum)")

    billing_account: BillingAccount = Field(default=BillingAccount(), description="Billing account of the project")

    users: List[ProjectUser] = Field(default=[], description="List of users and their permissions in the project")

    super_admin: Link[User] = Field(..., description="Super admin of the project")

    created_at: datetime = Field(default_factory=datetime.now, description="Date and time when the project was created")

    updated_at: datetime = Field(default_factory=datetime.now, description="Date and time when the project was last updated")

    @before_event([Save, Replace])
    def update_updated_at(self):
        self.updated_at = datetime.now()