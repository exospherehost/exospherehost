from pydantic import BaseModel
from .access_types import AccessTypeEnum
from typing import Any

class RegisterSatelliteResponse(BaseModel):
    id: str
    name: str
    friendly_name: str
    description: str
    access_type: AccessTypeEnum
    configs: dict[str, Any]
    inputs: dict[str, Any]
    metrics: dict[str, Any]
    outputs: dict[str, Any]
    project: str