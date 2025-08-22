from pymongo import IndexModel
from .base import BaseDatabaseModel
from ..state_status_enum import StateStatusEnum
from pydantic import Field
from beanie import Insert, PydanticObjectId, Replace, Save, before_event
from typing import Any, Optional
import hashlib
import json


class State(BaseDatabaseModel):
    node_name: str = Field(..., description="Name of the node of the state")
    namespace_name: str = Field(..., description="Name of the namespace of the state")
    identifier: str = Field(..., description="Identifier of the node for which state is created")
    graph_name: str = Field(..., description="Name of the graph template for this state")
    run_id: str = Field(..., description="Unique run ID for grouping states from the same graph execution")
    status: StateStatusEnum = Field(..., description="Status of the state")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")
    outputs: dict[str, Any] = Field(..., description="Outputs of the state")
    error: Optional[str] = Field(None, description="Error message")
    parents: dict[str, PydanticObjectId] = Field(default_factory=dict, description="Parents of the state")
    does_unites: bool = Field(default=False, description="Whether the state is unites others")
    state_fingerprint: str = Field(default="", description="Fingerprint of the state")

    @before_event([Insert, Replace, Save])
    def _generate_fingerprint(self):
        if not self.does_unites:
            self.state_fingerprint = ""
            return
        
        data = {
            "node_name": self.node_name,
            "namespace_name": self.namespace_name,
            "identifier": self.identifier,
            "graph_name": self.graph_name,
            "run_id": self.run_id,
            "parents": {key: str(value) for key, value in sorted(self.parents.items(), key=lambda x: x[0])}
        }
        self.state_fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    class Settings:
        indexes = [
            IndexModel(
                [
                    ("state_fingerprint", 1)
                ],
                unique=True,
                partialFilterExpression={
                    "does_unites": True
                }
            )
        ]