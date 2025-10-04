from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from croniter import croniter
from typing import Self, Optional
from zoneinfo import available_timezones

class TriggerTypeEnum(str, Enum):
    CRON = "CRON"

class TriggerStatusEnum(str, Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TRIGGERED = "TRIGGERED"
    TRIGGERING = "TRIGGERING"

class CronTrigger(BaseModel):
    expression: str = Field(..., description="Cron expression for the trigger")
    timezone: Optional[str] = Field(default="UTC", description="Timezone for the cron expression (e.g., 'America/New_York', 'Europe/London', 'UTC')")

    @field_validator("expression")
    @classmethod
    def validate_expression(cls, v: str) -> str:
        if not croniter.is_valid(v):
            raise ValueError("Invalid cron expression")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> str:
        if v is None:
            return "UTC"
        if v not in available_timezones():
            raise ValueError(f"Invalid timezone: {v}. Must be a valid IANA timezone (e.g., 'America/New_York', 'Europe/London', 'UTC')")
        return v

class Trigger(BaseModel):
    type: TriggerTypeEnum = Field(..., description="Type of the trigger")
    value: dict = Field(default_factory=dict, description="Value of the trigger")

    @model_validator(mode="after")
    def validate_trigger(self) -> Self:
        if self.type == TriggerTypeEnum.CRON:
            CronTrigger.model_validate(self.value)
        else:
            raise ValueError(f"Unsupported trigger type: {self.type}")
        return self