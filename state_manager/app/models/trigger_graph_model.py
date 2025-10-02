from pydantic import BaseModel, Field
from .state_status_enum import StateStatusEnum

class TriggerGraphRequestModel(BaseModel):
    store: dict[str, str] = Field(default_factory=dict, description="Store for the runtime")
    inputs: dict[str, str] = Field(default_factory=dict, description="Inputs for the graph execution")
    start_delay: int = Field(default=0, ge=0, description="Start delay in milliseconds")

class TriggerGraphResponseModel(BaseModel):
    status: StateStatusEnum = Field(..., description="Status of the states")
    run_id: str = Field(..., description="Unique run ID generated for this graph execution")