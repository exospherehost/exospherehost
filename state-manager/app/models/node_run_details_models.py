from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from .state_status_enum import StateStatusEnum


class NodeRunDetailsResponse(BaseModel):
    """Response model for node run details API"""
    id: str = Field(..., description="Unique identifier for the node (state ID)")
    node_name: str = Field(..., description="Name of the node")
    identifier: str = Field(..., description="Identifier of the node")
    graph_name: str = Field(..., description="Name of the graph template")
    run_id: str = Field(..., description="Run ID of the execution")
    status: StateStatusEnum = Field(..., description="Status of the state")
    inputs: Dict[str, Any] = Field(..., description="Inputs of the state")
    outputs: Dict[str, Any] = Field(..., description="Outputs of the state")
    error: Optional[str] = Field(None, description="Error message if any")
    parents: Dict[str, str] = Field(..., description="Parent node identifiers")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    enqueue_after: Optional[int] = Field(
        None,
        description=(
            "Unix time in milliseconds after which the state becomes eligible to be enqueued. "
            "This is the stored eligibility time (set by start delays, retry policies and requeue signals), "
            "not a guaranteed execution time: a worker picks the state up on its next poll after this instant."
        ),
    )
