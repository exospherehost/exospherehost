from pydantic import BaseModel, Field
from typing import Any
from .state_status_enum import StateStatusEnum
from datetime import datetime


class RequestStateModel(BaseModel):
    identifier: str = Field(..., description="Unique identifier of the node template within the graph template")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")


class ResponseStateModel(BaseModel):
    state_id: str = Field(..., description="ID of the state")
    node_name: str = Field(..., description="Name of the node of the state")
    identifier: str = Field(..., description="Identifier of the node for which state is created")
    graph_name: str = Field(..., description="Name of the graph template for this state")
    run_id: str = Field(..., description="Unique run ID for grouping states from the same graph execution")
    inputs: dict[str, Any] = Field(..., description="Inputs of the state")
    created_at: datetime = Field(..., description="Date and time when the state was created")


class CreateRequestModel(BaseModel):
    run_id: str = Field(..., description="Unique run ID for grouping states from the same graph execution")
    states: list[RequestStateModel] = Field(..., description="List of states")


class CreateResponseModel(BaseModel):
    status: StateStatusEnum = Field(..., description="Status of the state")
    states: list[ResponseStateModel] = Field(..., description="List of states")


class TriggerGraphRequestModel(BaseModel):
    states: list[RequestStateModel] = Field(..., description="List of states to create for the graph execution")


class TriggerGraphResponseModel(BaseModel):
    run_id: str = Field(..., description="Unique run ID generated for this graph execution")
    status: StateStatusEnum = Field(..., description="Status of the states")
    states: list[ResponseStateModel] = Field(..., description="List of created states")