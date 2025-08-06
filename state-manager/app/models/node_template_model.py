from pydantic import Field, BaseModel
from typing import Any, Optional, List, Set


class NodeTemplate(BaseModel):
    node_name: str = Field(..., description="Name of the node")
    namespace: str = Field(..., description="Namespace of the node")
    identifier: str = Field(..., description="Identifier of the node")
    inputs: dict[str, Any] = Field(..., description="Inputs of the node")
    store: dict[str, Any] = Field(..., description="Upsert data to store object for the node")
    next_nodes: Optional[Set[str]] = Field(None, description="Next nodes to execute")