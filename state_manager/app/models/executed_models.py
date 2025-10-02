from pydantic import BaseModel, Field
from typing import Any, List
from .state_status_enum import StateStatusEnum

class ExecutedRequestModel(BaseModel):
    outputs: List[dict[str, Any]] = Field(..., description="Outputs of the state")


class ExecutedResponseModel(BaseModel):
    status: StateStatusEnum = Field(..., description="Status of the state")