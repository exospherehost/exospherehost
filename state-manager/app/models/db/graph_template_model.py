from .base import BaseDatabaseModel
from pydantic import Field
from typing import Optional, List
from ..graph_template_validation_status import GraphTemplateValidationStatus
from ..node_template_model import NodeTemplate
from pymongo import IndexModel


class GraphTemplate(BaseDatabaseModel):
    name: str = Field(..., description="Name of the graph")
    namespace: str = Field(..., description="Namespace of the graph")
    nodes: List[NodeTemplate] = Field(..., description="Nodes of the graph")
    validation_status: GraphTemplateValidationStatus = Field(..., description="Validation status of the graph")
    validation_errors: Optional[List[str]] = Field(None, description="Validation errors of the graph")

    class Settings:
        indexes = [
            IndexModel(
                keys=[("name", 1), ("namespace", 1)],
                unique=True,
                name="unique_name_namespace"
            )
        ]