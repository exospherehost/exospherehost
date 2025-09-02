from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from .db.state import StateStatusEnum

class GraphNode(BaseModel):
    """Represents a node in the graph structure"""
    id: str = Field(..., description="Unique identifier for the node (state ID)")
    node_name: str = Field(..., description="Name of the node")
    identifier: str = Field(..., description="Identifier of the node")
    status: StateStatusEnum = Field(..., description="Status of the state")
    error: Optional[str] = Field(None, description="Error message if any")


class GraphEdge(BaseModel):
    """Represents an edge in the graph structure"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")


class GraphStructureResponse(BaseModel):
    """Response model for graph structure API"""
    root_states: List[GraphNode] = Field(..., description="Roots")
    graph_name: str = Field(..., description="Graph name")
    nodes: List[GraphNode] = Field(..., description="List of nodes in the graph")
    edges: List[GraphEdge] = Field(..., description="List of edges in the graph")
    node_count: int = Field(..., description="Number of nodes")
    edge_count: int = Field(..., description="Number of edges")
    execution_summary: Dict[str, int] = Field(..., description="Summary of execution statuses")
