from bson import ObjectId
from .base import BaseDatabaseModel
from ..state_status_enum import StateStatusEnum
from pydantic import Field
from typing import Any, Optional


class State(BaseDatabaseModel):

    node_name: str = Field(..., description="Name of the node of the state")
    namespace_name: str = Field(..., description="Name of the namespace of the state")
    identifier: str = Field(..., description="Identifier of the node for which state is created")
    graph_name: str = Field(..., description="Name of the graph template for this state")
    status: StateStatusEnum = Field(..., description="Status of the state")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")
    outputs: dict[str, Any] = Field(..., description="Outputs of the state")
    error: Optional[str] = Field(None, description="Error message")
    parents: dict[str, ObjectId] = Field(default_factory=dict, description="Parents of the state")