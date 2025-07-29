from pydantic import BaseModel, Field


class EnqueueRequestModel(BaseModel):
    nodes: list[str] = Field(..., description="Names of the nodes of the states")
    batch_size: int = Field(..., description="Batch size of the states")