from .base import BaseDatabaseModel
from ..state_status_enum import StateStatusEnum
from pydantic import Field
from typing import Any


class State(BaseDatabaseModel):

    node_name: str = Field(..., description="Name of the node of the state")
    namespace_name: str = Field(..., description="Name of the namespace of the state")
    status: StateStatusEnum = Field(..., description="Status of the state")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")
    outputs: dict[str, Any] = Field(..., description="Outputs of the state")