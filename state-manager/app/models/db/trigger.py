from pydantic import Field
from beanie import Document
from typing import Optional

from pymongo import IndexModel
from ..trigger_models import TriggerTypeEnum, TriggerStatusEnum
from datetime import datetime

class DatabaseTriggers(Document):
    type: TriggerTypeEnum = Field(..., description="Type of the trigger")
    expression: Optional[str] = Field(default=None, description="Expression of the trigger")
    graph_name: str = Field(..., description="Name of the graph")
    trigger_time: datetime = Field(..., description="Trigger time of the trigger")
    trigger_status: TriggerStatusEnum = Field(..., description="Status of the trigger")

    class Settings: 
        indexes = [
            IndexModel(
                [
                    ("trigger_time", -1),
                ],
                name="idx_trigger_time"
            )
        ]
