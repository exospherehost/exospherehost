import jsonschema

from beanie import Document, before_event, Replace, Save, Link
from datetime import datetime
from pydantic import Field, field_validator
from .access_types import AccessTypeEnum
from docker_image import reference
from typing import Optional, Any
from pymongo import IndexModel, ASCENDING

from app.project.models.project_database_model import Project


class Satellite(Document):

    name: str = Field(..., description="Name of the satellite")

    friendly_name: str = Field(..., description="Friendly name of the satellite")

    description: str = Field(..., description="Description of the satellite")

    access_type: AccessTypeEnum = Field(..., description="Access type of the satellite")

    configs: dict[str, Any] = Field(..., description="Configurations of the satellite, a valid jsonschema object for the configs")
    
    inputs: dict[str, Any] = Field(..., description="Input data fothe satellite, a valid jsonschema object for the inputs")
    
    metrics: dict[str, Any] = Field(..., description="Metrics of the satellite, a valid jsonschema object for the metrics")
   
    outputs: dict[str, Any] = Field(..., description="Outputs of the satellite, a valid jsonschema object for the outputs")

    project: Link[Project] = Field(..., description="Project of the satellite")

    project_name: str = Field(..., description="Name of the project of the satellite")

    created_at: datetime = Field(default_factory=datetime.now, description="Date and time when the satellite was created")

    updated_at: datetime = Field(default_factory=datetime.now, description="Date and time when the satellite was last updated")

    image_uri: Optional[str] = Field(None, description="OCI/Docker image URI for the satellite, if not provided autoscalling and dynamic scaling would not be available")

    timeout: Optional[int] = Field(None, description="Timeout of the satellite in seconds")

    @field_validator("configs", "inputs", "metrics", "outputs")
    def validate_jsonschema(cls, v: dict[str, Any]) -> dict[str, Any]:
        validator = jsonschema.validators.validator_for(v)

        try:
            validator.check_schema(v)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Invalid JSON schema: {e.message}")

        return v
    
    @field_validator("image_uri")
    def validate_image_uri(cls, v: str) -> str:
        if not v:
            return v
        try:
            reference.Reference.parse(v)
        except Exception as e:
            raise ValueError(f"Invalid image URI: {e.message}")
        return v
    
    @field_validator("name")
    def validate_name(cls, v: str) -> str:

        not_allowed_chars = ["/", ".", " "]

        if not v:
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name cannot be longer than 100 characters")
        if any(char in not_allowed_chars for char in v):
            raise ValueError("Name cannot contain the following characters: /, ., or whitespace")
        return v

    class Settings:
        name = "Satellites"
        indexes = [
            IndexModel([("name", ASCENDING), ("project", ASCENDING)], unique=True)
        ]

    @before_event([Save, Replace])
    def update_updated_at(self):
        self.updated_at = datetime.now()