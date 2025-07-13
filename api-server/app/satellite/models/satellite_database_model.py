import jsonschema

from beanie import Document, Indexed, before_event, Replace, Save, Link
from datetime import datetime
from pydantic import Field, Any, field_validator
from .access_types import AccessTypeEnum

from app.project.models.project_database_model import Project


class Satellite(Document):

    name: Indexed(str, unique=True) = Field(..., description="Name of the satellite")

    friendly_name: str = Field(..., description="Friendly name of the satellite")

    description: str = Field(..., description="Description of the satellite")

    access_type: AccessTypeEnum = Field(..., description="Access type of the satellite")

    configs: dict[str, Any] = Field(..., description="Configurations of the satellite, a valid jsonschema object for the configs")
    inputs: dict[str, Any] = Field(..., description="Input data fothe satellite, a valid jsonschema object for the inputs")
    metrics: dict[str, Any] = Field(..., description="Metrics of the satellite, a valid jsonschema object for the metrics")
    outputs: dict[str, Any] = Field(..., description="Outputs of the satellite, a valid jsonschema object for the outputs")

    project: Link[Project] = Field(..., description="Project of the satellite")

    created_at: datetime = Field(default_factory=datetime.now, description="Date and time when the satellite was created")

    updated_at: datetime = Field(default_factory=datetime.now, description="Date and time when the satellite was last updated")


    @field_validator("configs", "inputs", "metrics", "outputs")
    def validate_jsonschema(cls, v: dict[str, Any]) -> dict[str, Any]:
        validator = jsonschema.validators.validator_for(v)

        try:
            validator.check_schema(v)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Invalid JSON schema: {e.message}")

        return v


    @before_event([Save, Replace])
    def update_updated_at(self):
        self.updated_at = datetime.now()