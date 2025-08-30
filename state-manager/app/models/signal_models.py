from pydantic import BaseModel, Field
from .state_status_enum import StateStatusEnum
from typing import Any


class SignalResponseModel(BaseModel):
    enqueue_after: int = Field(..., description="Unix time in milliseconds after which the state should be re-enqueued")
    status: StateStatusEnum = Field(..., description="Status of the state")

class PruneRequestModel(BaseModel):
    data: dict[str, Any] = Field(..., description="Data of the state")

class ReEnqueueAfterRequestModel(BaseModel):
    enqueue_after: int = Field(..., gt=0, description="Duration in milliseconds to delay the re-enqueuing of the state")