from .node_template_model import NodeTemplate
from pydantic import BaseModel
from typing import List
from datetime import datetime


class UpsertGraphTemplateRequest(BaseModel):
    name: str
    namespace: str
    nodes: List[NodeTemplate]


class UpsertGraphTemplateResponse(BaseModel):
    name: str
    namespace: str
    nodes: List[NodeTemplate]
    created_at: datetime
    updated_at: datetime