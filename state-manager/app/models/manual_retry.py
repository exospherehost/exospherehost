from pydantic import BaseModel, Field
from .state_status_enum import StateStatusEnum


class ManualRetryRequestModel(BaseModel):
    fanout_id: str = Field(..., description="Fanout ID of the state")


class ManualRetryResponseModel(BaseModel):
    id: str = Field(..., description="ID of the state")
    status: StateStatusEnum = Field(..., description="Status of the state")
