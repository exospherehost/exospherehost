"""
Response models for state listing operations
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class RunListItem(BaseModel):
    """Model for a single run in a list"""
    run_id: str = Field(..., description="The run ID")
    success_count: int = Field(..., description="Number of success states")
    pending_count: int = Field(..., description="Number of pending states")
    failed_count: int = Field(..., description="Number of failed states")
    total_count: int = Field(..., description="Total number of states")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class RunsResponse(BaseModel):
    """Response model for fetching current states"""
    namespace: str = Field(..., description="The namespace")
    total: int = Field(..., description="Number of runs")
    page: int = Field(..., description="Page number")
    size: int = Field(..., description="Page size")
    runs: List[RunListItem] = Field(..., description="List of runs")
