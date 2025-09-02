from pydantic import Field, BaseModel, field_validator
from typing import Any, Optional, List
from .dependent_string import DependentString
from enum import Enum


class UnitesStrategyEnum(str, Enum):
    ALL_SUCCESS = "ALL_SUCCESS"
    ALL_DONE = "ALL_DONE"


class Unites(BaseModel):
    identifier: str = Field(..., description="Identifier of the node")
    strategy: UnitesStrategyEnum = Field(default=UnitesStrategyEnum.ALL_SUCCESS, description="Strategy of the unites")


class NodeTemplate(BaseModel):
    node_name: str = Field(..., description="Name of the node")
    namespace: str = Field(..., description="Namespace of the node")
    identifier: str = Field(..., description="Identifier of the node")
    inputs: dict[str, Any] = Field(..., description="Inputs of the node")
    next_nodes: Optional[List[str]] = Field(None, description="Next nodes to execute")
    unites: Optional[Unites] = Field(None, description="Unites of the node")

    @field_validator('node_name')
    @classmethod
    def validate_node_name(cls, v: str) -> str:
        trimmed_v = v.strip()
        if trimmed_v == "" or trimmed_v is None:
            raise ValueError("Node name cannot be empty")
        return trimmed_v
    
    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        trimmed_v = v.strip()
        if trimmed_v == "" or trimmed_v is None:
            raise ValueError("Node identifier cannot be empty")
        elif trimmed_v == "store":
            raise ValueError("Node identifier cannot be reserved word 'store'")
        return trimmed_v
    
    @field_validator('next_nodes')
    @classmethod
    def validate_next_nodes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        identifiers = set()
        errors = []
        trimmed_v = []

        if v is not None:
            for next_node_identifier in v:
                trimmed_next_node_identifier = next_node_identifier.strip()
                
                if trimmed_next_node_identifier == "" or trimmed_next_node_identifier is None:
                    errors.append("Next node identifier cannot be empty")
                    continue

                if trimmed_next_node_identifier in identifiers:
                    errors.append(f"Next node identifier {trimmed_next_node_identifier} is not unique")
                    continue

                identifiers.add(trimmed_next_node_identifier)
                trimmed_v.append(trimmed_next_node_identifier)
        if errors:
            raise ValueError("\n".join(errors))
        return trimmed_v
    
    @field_validator('unites')
    @classmethod
    def validate_unites(cls, v: Optional[Unites]) -> Optional[Unites]:
        trimmed_v = v
        if v is not None:
            trimmed_v = Unites(identifier=v.identifier.strip(), strategy=v.strategy)
            if trimmed_v.identifier == "" or trimmed_v.identifier is None:
                raise ValueError("Unites identifier cannot be empty")
        return trimmed_v
    
    def get_dependent_strings(self) -> list[DependentString]:
        dependent_strings = []
        for input_value in self.inputs.values():
            if not isinstance(input_value, str):
                raise ValueError(f"Input {input_value} is not a string")
            dependent_strings.append(DependentString.create_dependent_string(input_value))
        return dependent_strings