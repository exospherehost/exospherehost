"""
Response models for listing operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .db.registered_node import RegisteredNode
from .db.graph_template_model import GraphTemplate


class ListRegisteredNodesResponse(BaseModel):
    """Response model for listing registered nodes"""
    namespace: str = Field(..., description="The namespace")
    count: int = Field(..., description="Number of registered nodes")
    nodes: List[RegisteredNode] = Field(..., description="List of registered nodes")


class ListGraphTemplatesResponse(BaseModel):
    """Response model for listing graph templates"""
    namespace: str = Field(..., description="The namespace")
    count: int = Field(..., description="Number of graph templates")
    templates: List[GraphTemplate] = Field(..., description="List of graph templates")


class NamespaceSummaryResponse(BaseModel):
    """Response model for namespace summary"""
    namespace: str = Field(..., description="The namespace")
    registered_nodes_count: int = Field(..., description="Number of registered nodes")
    graph_templates_count: int = Field(..., description="Number of graph templates")
    total_states_count: int = Field(..., description="Total number of states")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
