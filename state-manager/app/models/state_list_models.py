"""
Response models for state listing operations
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from enum import Enum

class RunStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"

class RunListItem(BaseModel):
    """Model for a single run in a list"""
    run_id: str = Field(..., description="The run ID")
    graph_name: str = Field(..., description="The graph name")
    success_count: int = Field(..., description="Number of success states")
    pending_count: int = Field(..., description="Number of pending states")
    errored_count: int = Field(..., description="Number of errored states")
    retried_count: int = Field(..., description="Number of retried states")
    total_count: int = Field(..., description="Total number of states")
    status: RunStatusEnum = Field(..., description="Status of the run")
    created_at: datetime = Field(..., description="Creation timestamp")

class RunsResponse(BaseModel):
    """Response model for fetching current states"""
    namespace: str = Field(..., description="The namespace")
    total: int = Field(..., description="Number of runs")
    page: int = Field(..., description="Page number")
    size: int = Field(..., description="Page size")
    runs: List[RunListItem] = Field(..., description="List of runs")
