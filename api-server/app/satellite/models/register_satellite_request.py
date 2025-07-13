from pydantic import BaseModel
from .access_types import AccessTypeEnum
from typing import Any

class RegisterSatelliteRequest(BaseModel):
    friendly_name: str
    description: str
    access_type: AccessTypeEnum
    image_uri: str
    timeout: int
    configs: dict[str, Any]
    inputs: dict[str, Any]
    metrics: dict[str, Any]
    outputs: dict[str, Any]