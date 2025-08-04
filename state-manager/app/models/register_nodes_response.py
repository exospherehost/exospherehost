from pydantic import BaseModel, Field
from typing import List


class RegisteredNodeModel(BaseModel):
    name: str = Field(..., description="Name of the registered node")
    namespace: str = Field(..., description="Namespace of the registered node")


class RegisterNodesResponseModel(BaseModel):
    runtime_name: str = Field(..., description="Name of the runtime that registered the nodes")
    runtime_namespace: str = Field(..., description="Namespace of the runtime")
    registered_nodes: List[RegisteredNodeModel] = Field(..., description="List of successfully registered nodes")