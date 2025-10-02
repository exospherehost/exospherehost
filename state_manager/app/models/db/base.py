from abc import ABC
from beanie import Document, before_event, Replace, Save
from datetime import datetime
from pydantic import Field


class BaseDatabaseModel(ABC, Document):

    created_at: datetime = Field(default_factory=datetime.now, description="Date and time when the model was created")

    updated_at: datetime = Field(default_factory=datetime.now, description="Date and time when the model was last updated")

    @before_event([Save, Replace])
    def update_updated_at(self):
        self.updated_at = datetime.now()