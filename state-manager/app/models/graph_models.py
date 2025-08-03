from .node_template_model import NodeTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .graph_template_validation_status import GraphTemplateValidationStatus


class UpsertGraphTemplateRequest(BaseModel):
    nodes: List[NodeTemplate] = Field(..., description="List of node templates that define the graph structure")


class UpsertGraphTemplateResponse(BaseModel):
    nodes: List[NodeTemplate] = Field(..., description="List of node templates that define the graph structure")
    created_at: datetime = Field(..., description="Timestamp when the graph template was created")
    updated_at: datetime = Field(..., description="Timestamp when the graph template was last updated")
    validation_status: GraphTemplateValidationStatus = Field(..., description="Current validation status of the graph template")
    validation_errors: Optional[List[str]] = Field(None, description="List of validation errors if the graph template is invalid")
