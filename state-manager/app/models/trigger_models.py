from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from croniter import croniter
from typing import Self

class TriggerTypeEnum(str, Enum):
    CRON = "CRON"

class CronTrigger(BaseModel):
    expression: str = Field(..., description="Cron expression for the trigger")

    @field_validator("expression")
    @classmethod
    def validate_expression(cls, v: str) -> str:
        if not croniter.is_valid(v):
            raise ValueError("Invalid cron expression")
        return v

class Trigger(BaseModel):
    type: TriggerTypeEnum = Field(..., description="Type of the trigger")
    value: dict[str, str] = Field(default={}, description="Value of the trigger")

    @model_validator(mode="after")
    def validate_trigger(self) -> Self:
        if self.type == TriggerTypeEnum.CRON:
            CronTrigger.model_validate(self.value)
        return self