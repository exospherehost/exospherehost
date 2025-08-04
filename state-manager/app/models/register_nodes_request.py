from pydantic import BaseModel, Field
from typing import Any, List


class NodeRegistrationModel(BaseModel):
    name: str = Field(..., description="Unique name of the node")
    namespace: str = Field(..., description="Namespace of the node")
    inputs_schema: dict[str, Any] = Field(..., description="JSON schema for node inputs")
    outputs_schema: dict[str, Any] = Field(..., description="JSON schema for node outputs")


class RegisterNodesRequestModel(BaseModel):
    runtime_name: str = Field(..., description="Name of the runtime registering the nodes")
    runtime_namespace: str = Field(..., description="Namespace of the runtime")
    nodes: List[NodeRegistrationModel] = Field(..., description="List of nodes to register") 