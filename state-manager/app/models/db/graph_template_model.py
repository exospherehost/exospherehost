import base64
import time
import asyncio

from .base import BaseDatabaseModel
from pydantic import Field, field_validator, PrivateAttr, model_validator
from typing import Optional, List, Self
from ..graph_template_validation_status import GraphTemplateValidationStatus
from ..node_template_model import NodeTemplate
from pymongo import IndexModel
from typing import Dict
from app.utils.encrypter import get_encrypter


class GraphTemplate(BaseDatabaseModel):
    name: str = Field(..., description="Name of the graph")
    namespace: str = Field(..., description="Namespace of the graph")
    nodes: List[NodeTemplate] = Field(..., description="Nodes of the graph")
    validation_status: GraphTemplateValidationStatus = Field(..., description="Validation status of the graph")
    validation_errors: Optional[List[str]] = Field(None, description="Validation errors of the graph")
    secrets: Dict[str, str] = Field(default_factory=dict, description="Secrets of the graph")
    _node_by_identifier: Dict[str, NodeTemplate] | None = PrivateAttr(default=None)

    class Settings:
        indexes = [
            IndexModel(
                keys=[("name", 1), ("namespace", 1)],
                unique=True,
                name="unique_name_namespace"
            )
        ]

    def _build_node_by_identifier(self) -> None:
        self._node_by_identifier = {node.identifier: node for node in self.nodes}

    def get_node_by_identifier(self, identifier: str) -> NodeTemplate | None:
        """Get a node by its identifier using O(1) dictionary lookup."""
        if self._node_by_identifier is None:
            self._build_node_by_identifier()

        assert self._node_by_identifier is not None
        return self._node_by_identifier.get(identifier)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v == "" or v is None:
            raise ValueError("Name cannot be empty")
        return v
    
    @field_validator('namespace')
    @classmethod
    def validate_namespace(cls, v: str) -> str:
        if v == "" or v is None:
            raise ValueError("Namespace cannot be empty")
        return v

    @field_validator('secrets')
    @classmethod
    def validate_secrets(cls, v: Dict[str, str]) -> Dict[str, str]:
        for secret_name, secret_value in v.items():
            if not secret_name or not secret_value:
                raise ValueError("Secrets cannot be empty")
            if not isinstance(secret_name, str):
                raise ValueError("Secret name must be a string")
            if not isinstance(secret_value, str):
                raise ValueError("Secret value must be a string")
            cls._validate_secret_value(secret_value)
            
        return v
    
    @model_validator(mode='after')
    def validate_nodes(self) -> Self:
        for node in self.nodes:
            if node.namespace != self.namespace:
                raise ValueError(f"Node namespace {node.namespace} does not match graph namespace {self.namespace}")
        return self
    
    @field_validator('nodes')
    @classmethod
    def validate_unique_identifiers(cls, v: List[NodeTemplate]) -> List[NodeTemplate]:
        identifiers = set()
        errors = []
        for node in v:
            if node.identifier in identifiers:
                errors.append(f"Node identifier {node.identifier} is not unique")
            identifiers.add(node.identifier)
        if errors:
            raise ValueError("\n".join(errors))
        return v
    
    @field_validator('nodes')
    @classmethod
    def validate_next_nodes_identifiers_exist(cls, v: List[NodeTemplate]) -> List[NodeTemplate]:
        identifiers = set()
        for node in v:
            identifiers.add(node.identifier)

        errors = []    
        for node in v:
            if node.next_nodes:
                for next_node in node.next_nodes:
                    if next_node not in identifiers:
                        errors.append(f"Node identifier {next_node} does not exist in the graph")
        if errors:
            raise ValueError("\n".join(errors))
        return v
    
    @classmethod
    def _validate_secret_value(cls, secret_value: str) -> None:
        # Check minimum length for AES-GCM encrypted string
        # 12 bytes nonce + minimum ciphertext + base64 encoding
        if len(secret_value) < 32:  # Minimum length for encrypted string
            raise ValueError("Value appears to be too short for an encrypted string")
               
        # Try to decode as base64 to ensure it's valid
        try:
            decoded = base64.urlsafe_b64decode(secret_value)
            if len(decoded) < 12:
                raise ValueError("Decoded value is too short to contain valid nonce")
        except Exception:
            raise ValueError("Value is not valid URL-safe base64 encoded")
        
    def set_secrets(self, secrets: Dict[str, str]) -> "GraphTemplate":
        self.secrets = {secret_name: get_encrypter().encrypt(secret_value) for secret_name, secret_value in secrets.items()}
        return self
    
    def get_secrets(self) -> Dict[str, str]:
        if not self.secrets:
            return {}
        return {secret_name: get_encrypter().decrypt(secret_value) for secret_name, secret_value in self.secrets.items()}
    
    def get_secret(self, secret_name: str) -> str | None:
        if not self.secrets:
            return None
        if secret_name not in self.secrets:
            return None
        return get_encrypter().decrypt(self.secrets[secret_name])

    def is_valid(self) -> bool:
        return self.validation_status == GraphTemplateValidationStatus.VALID

    def is_validating(self) -> bool:
        return self.validation_status in (GraphTemplateValidationStatus.ONGOING, GraphTemplateValidationStatus.PENDING)
    
    @staticmethod
    async def get(namespace: str, graph_name: str) -> "GraphTemplate":
        graph_template = await GraphTemplate.find_one(GraphTemplate.namespace == namespace, GraphTemplate.name == graph_name)
        if not graph_template:
            raise ValueError(f"Graph template not found for namespace: {namespace} and graph name: {graph_name}")
        return graph_template
    
    @staticmethod
    async def get_valid(namespace: str, graph_name: str, polling_interval: float = 1.0, timeout: float = 300.0) -> "GraphTemplate":
        # Validate polling_interval and timeout
        if polling_interval <= 0:
            raise ValueError("polling_interval must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        
        # Coerce polling_interval to a sensible minimum
        if polling_interval < 0.1:
            polling_interval = 0.1
        
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            graph_template = await GraphTemplate.get(namespace, graph_name)
            if graph_template.is_valid():
                return graph_template
            if graph_template.is_validating():
                await asyncio.sleep(polling_interval)
            else:
                raise ValueError(f"Graph template is in a non-validating state: {graph_template.validation_status.value} for namespace: {namespace} and graph name: {graph_name}")
        raise ValueError(f"Graph template is not valid for namespace: {namespace} and graph name: {graph_name} after {timeout} seconds")