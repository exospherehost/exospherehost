from .base import BaseDatabaseModel
from pydantic import Field
from typing import Any


class RegisteredNode(BaseDatabaseModel):
    name: str = Field(..., description="Unique name of the registered node")
    namespace: str = Field(..., description="Namespace of the registered node")
    runtime_name: str = Field(..., description="Name of the runtime that registered this node")
    runtime_namespace: str = Field(..., description="Namespace of the runtime that registered this node")
    inputs_schema: dict[str, Any] = Field(..., description="JSON schema for node inputs")
    outputs_schema: dict[str, Any] = Field(..., description="JSON schema for node outputs") 