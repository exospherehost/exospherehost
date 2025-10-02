from pydantic import BaseModel, Field
from .state_status_enum import StateStatusEnum


class ErroredRequestModel(BaseModel):
    error: str = Field(..., description="Error message")


class ErroredResponseModel(BaseModel):
    status: StateStatusEnum = Field(..., description="Status of the state")
    retry_created: bool = Field(default=False, description="Whether a retry state was created")