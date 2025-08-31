from pymongo import IndexModel
from .base import BaseDatabaseModel
from ..state_status_enum import StateStatusEnum
from pydantic import Field
from beanie import Insert, PydanticObjectId, Replace, Save, before_event
from pymongo.results import InsertManyResult
from typing import Any, Optional
import hashlib
import json
import time

class State(BaseDatabaseModel):
    node_name: str = Field(..., description="Name of the node of the state")
    namespace_name: str = Field(..., description="Name of the namespace of the state")
    identifier: str = Field(..., description="Identifier of the node for which state is created")
    graph_name: str = Field(..., description="Name of the graph template for this state")
    run_id: str = Field(..., description="Unique run ID for grouping states from the same graph execution")
    status: StateStatusEnum = Field(..., description="Status of the state")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")
    outputs: dict[str, Any] = Field(..., description="Outputs of the state")
    data: dict[str, Any] = Field(default_factory=dict, description="Data of the state (could be used to save pruned meta data)")
    error: Optional[str] = Field(None, description="Error message")
    parents: dict[str, PydanticObjectId] = Field(default_factory=dict, description="Parents of the state")
    does_unites: bool = Field(default=False, description="Whether this state unites other states")
    state_fingerprint: str = Field(default="", description="Fingerprint of the state")
    enqueue_after: int = Field(default_factory=lambda: int(time.time() * 1000), gt=0, description="Unix time in milliseconds after which the state should be enqueued")
    retry_count: int = Field(default=0, description="Number of times the state has been retried")
    
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
            "retry_count": self.retry_count,
            "parents": {k: str(v) for k, v in self.parents.items()},
        }
        payload = json.dumps(
            data,
            sort_keys=True,            # canonical key ordering at all levels
            separators=(",", ":"),     # no whitespace variance
            ensure_ascii=True,         # normalized non-ASCII escapes
        ).encode("utf-8")
        self.state_fingerprint = hashlib.sha256(payload).hexdigest()    
    
    @classmethod
    async def insert_many(cls, documents: list["State"]) -> InsertManyResult:
        """Override insert_many to ensure fingerprints are generated before insertion."""
        # Generate fingerprints for states that need them
        for state in documents:
            state._generate_fingerprint()
        
        return await super().insert_many(documents) # type: ignore
        
    class Settings:
        indexes = [
            IndexModel(
                [
                    ("state_fingerprint", 1)
                ],
                unique=True,
                name="uniq_state_fingerprint_unites",
                partialFilterExpression={
                    "does_unites": True
                }
            ),
            IndexModel(
                [
                    ("enqueue_after", 1),
                    ("status", 1),
                    ("namespace_name", 1),
                    ("node_name", 1),
                ],
                name="idx_enqueue_after"
            )
        ]