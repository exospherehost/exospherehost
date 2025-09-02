from beanie import Document
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel


class Run(Document):
    run_id: str = Field(..., description="The run ID")
    graph_name: str = Field(default="", description="The graph name")
    namespace_name: str = Field(default="", description="The namespace name")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    class Settings:
        indexes = [
            IndexModel(
                keys=[("created_at", -1)],
                name="created_at_index"
            ),
            IndexModel(
                keys=[("run_id", 1)],
                unique=True,
                name="run_id_index"
            )
        ]