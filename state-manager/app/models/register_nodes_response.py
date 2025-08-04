from pydantic import BaseModel, Field
from typing import Any, List


class RegisteredNodeModel(BaseModel):
    name: str = Field(..., description="Name of the registered node")
    inputs_schema: dict[str, Any] = Field(..., description="Inputs for the registered node")
    outputs_schema: dict[str, Any] = Field(..., description="Outputs for the registered node")


class RegisterNodesResponseModel(BaseModel):
    runtime_name: str = Field(..., description="Name of the runtime that registered the nodes")
    registered_nodes: List[RegisteredNodeModel] = Field(..., description="List of successfully registered nodes")