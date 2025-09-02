from .node_template_model import NodeTemplate
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from .graph_template_validation_status import GraphTemplateValidationStatus
from .retry_policy_model import RetryPolicyModel
from .store_config_model import StoreConfig


class UpsertGraphTemplateRequest(BaseModel):
    secrets: Dict[str, str] = Field(..., description="Dictionary of secrets that are used while graph execution")
    nodes: List[NodeTemplate] = Field(..., description="List of node templates that define the graph structure")
    retry_policy: RetryPolicyModel = Field(default_factory=RetryPolicyModel, description="Retry policy of the graph")
    store_config: StoreConfig = Field(default_factory=StoreConfig, description="Store config of the graph")


class UpsertGraphTemplateResponse(BaseModel):
    nodes: List[NodeTemplate] = Field(..., description="List of node templates that define the graph structure")
    secrets: Dict[str, bool] = Field(..., description="Dictionary of secrets that are used while graph execution")
    retry_policy: RetryPolicyModel = Field(default_factory=RetryPolicyModel, description="Retry policy of the graph")
    store_config: StoreConfig = Field(default_factory=StoreConfig, description="Store config of the graph")
    created_at: datetime = Field(..., description="Timestamp when the graph template was created")
    updated_at: datetime = Field(..., description="Timestamp when the graph template was last updated")
    validation_status: GraphTemplateValidationStatus = Field(..., description="Current validation status of the graph template")
    validation_errors: Optional[List[str]] = Field(None, description="List of validation errors if the graph template is invalid")
