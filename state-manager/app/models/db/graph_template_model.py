import base64

from .base import BaseDatabaseModel
from pydantic import Field, field_validator
from typing import Optional, List
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

    class Settings:
        indexes = [
            IndexModel(
                keys=[("name", 1), ("namespace", 1)],
                unique=True,
                name="unique_name_namespace"
            )
        ]

    @property
    def node_identifier_map(self) -> Dict[str, NodeTemplate]:
        """Create a dictionary mapping node identifiers to nodes for O(1) lookup."""
        return {node.identifier: node for node in self.nodes}

    def get_node_by_identifier(self, identifier: str) -> NodeTemplate | None:
        """Get a node by its identifier using O(1) dictionary lookup."""
        node_map = self.node_identifier_map
        if identifier not in node_map:
            return None
        return node_map[identifier]

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