from pydantic import BaseModel
from .billing_account import BillingAccount
from .project_status_enum import ProjectStatusEnum
from datetime import datetime


class CreateProjectResponse(BaseModel):
    id: str
    name: str
    status: ProjectStatusEnum
    billing_account: BillingAccount
    super_admin: str
    created_at: datetime
    updated_at: datetime