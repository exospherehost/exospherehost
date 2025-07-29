from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime


class StateModel(BaseModel):
    state_id: str = Field(..., description="ID of the state")
    node_name: str = Field(..., description="Name of the node of the state")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")
    created_at: datetime = Field(..., description="Date and time when the state was created")


class EnqueueResponseModel(BaseModel):

    count: int = Field(..., description="Count of states")
    namespace: str = Field(..., description="ID of the namespace")
    status: str = Field(..., description="Status of the state")
    states: list[StateModel] = Field(..., description="List of states")
