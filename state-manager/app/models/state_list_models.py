"""
Response models for state listing operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from beanie import PydanticObjectId

from .state_status_enum import StateStatusEnum


class StateListItem(BaseModel):
    """Model for a single state in a list"""
    id: PydanticObjectId = Field(..., description="State ID")
    node_name: str = Field(..., description="Name of the node")
    namespace_name: str = Field(..., description="Namespace name")
    identifier: str = Field(..., description="Node identifier")
    graph_name: str = Field(..., description="Graph name")
    run_id: str = Field(..., description="Run ID")
    status: StateStatusEnum = Field(..., description="State status")
    inputs: dict[str, Any] = Field(..., description="State inputs")
    outputs: dict[str, Any] = Field(..., description="State outputs")
    error: Optional[str] = Field(None, description="Error message")
    parents: dict[str, PydanticObjectId] = Field(default_factory=dict, description="Parent state IDs")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class StatesByRunIdResponse(BaseModel):
    """Response model for fetching states by run ID"""
    namespace: str = Field(..., description="The namespace")
    run_id: str = Field(..., description="The run ID")
    count: int = Field(..., description="Number of states")
    states: List[StateListItem] = Field(..., description="List of states")


class CurrentStatesResponse(BaseModel):
    """Response model for fetching current states"""
    namespace: str = Field(..., description="The namespace")
    count: int = Field(..., description="Number of states")
    states: List[StateListItem] = Field(..., description="List of states")
    run_ids: List[str] = Field(..., description="List of unique run IDs")
