"""
Integration tests for the complete state-manager workflow using local code.
"""
import pytest
import uuid
from typing import List
from unittest.mock import patch

from app.models.register_nodes_request import RegisterNodesRequestModel
from app.models.graph_models import UpsertGraphTemplateRequest
from app.models.create_models import CreateRequestModel, RequestStateModel
from app.models.executed_models import ExecutedRequestModel
from app.models.enqueue_request import EnqueueRequestModel
from app.models.state_status_enum import StateStatusEnum
from app.config.settings import Settings


class TestFullWorkflowIntegration:
    """Integration tests for the complete state-manager workflow using local code."""

    def test_register_nodes_model_validation(
        self, 
        test_namespace: str,
        test_api_key: str, 
        test_runtime_name: str,
        sample_node_registration
    ):
        """Test registering nodes model validation."""
        
        # Prepare the request
        request_data = RegisterNodesRequestModel(
            runtime_name=test_runtime_name,
            nodes=[sample_node_registration]
        )
        
        # Verify the model is valid
        assert request_data.runtime_name == test_runtime_name
        assert len(request_data.nodes) == 1
        assert request_data.nodes[0].name == "TestNode"
        assert request_data.nodes[0].inputs_schema is not None
        assert request_data.nodes[0].outputs_schema is not None

    def test_upsert_graph_template_model_validation(
        self, 
        test_namespace: str,
        test_api_key: str, 
        test_graph_name: str,
        sample_graph_nodes: List
    ):
        """Test creating a graph template model validation."""
        
        # Prepare the request
        request_data = UpsertGraphTemplateRequest(
            secrets={"test_secret": "secret_value"},
            nodes=sample_graph_nodes
        )
        
        # Verify the model is valid
        assert request_data.secrets == {"test_secret": "secret_value"}
        assert len(request_data.nodes) == 2
        assert request_data.nodes[0].identifier == "node1"
        assert request_data.nodes[1].identifier == "node2"

    def test_create_states_model_validation(
        self, 
        test_namespace: str,
        test_api_key: str, 
        test_graph_name: str
    ):
        """Test creating states model validation."""
        
        # Prepare the request
        request_data = CreateRequestModel(
            run_id=str(uuid.uuid4()),
            states=[
                RequestStateModel(
                    identifier="node1",
                    inputs={
                        "input1": "test_value",
                        "input2": 42
                    }
                )
            ]
        )
        
        # Verify the model is valid
        assert request_data.run_id is not None
        assert len(request_data.states) == 1
        assert request_data.states[0].identifier == "node1"
        assert request_data.states[0].inputs["input1"] == "test_value"
        assert request_data.states[0].inputs["input2"] == 42

    def test_enqueue_states_model_validation(
        self, 
        test_namespace: str,
        test_api_key: str
    ):
        """Test enqueuing states model validation."""
        
        # Prepare the request
        request_data = EnqueueRequestModel(
            nodes=["TestNode"],
            batch_size=1
        )
        
        # Verify the model is valid
        assert request_data.nodes == ["TestNode"]
        assert request_data.batch_size == 1

    def test_node_template_model_validation(self, test_namespace: str):
        """Test NodeTemplate model validation."""
        from app.models.graph_models import NodeTemplate
        
        # Create a node template
        node = NodeTemplate(
            node_name="TestNode",
            namespace=test_namespace,
            identifier="node1",
            inputs={
                "input1": "test_value",
                "input2": 42
            },
            next_nodes=["node2"]
        )
        
        # Verify the model is valid
        assert node.node_name == "TestNode"
        assert node.namespace == test_namespace
        assert node.identifier == "node1"
        assert node.inputs["input1"] == "test_value"
        assert node.inputs["input2"] == 42
        assert node.next_nodes == ["node2"]

    def test_full_workflow_model_validation(
        self, 
        test_namespace: str,
        test_api_key: str, 
        test_graph_name: str,
        test_runtime_name: str,
        sample_node_registration,
        sample_graph_nodes: List
    ):
        """Test the complete workflow model validation."""
        
        # Step 1: Register nodes model validation
        self.test_register_nodes_model_validation(
            test_namespace, test_api_key, test_runtime_name, sample_node_registration
        )
        
        # Step 2: Create graph template model validation
        self.test_upsert_graph_template_model_validation(
            test_namespace, test_api_key, test_graph_name, sample_graph_nodes
        )
        
        # Step 3: Create states model validation
        self.test_create_states_model_validation(
            test_namespace, test_api_key, test_graph_name
        )
        
        # Step 4: Enqueue states model validation
        self.test_enqueue_states_model_validation(
            test_namespace, test_api_key
        )
        
        # Step 5: Node template model validation
        self.test_node_template_model_validation(test_namespace)
        
        # All steps completed successfully
        assert True

    def test_settings_integration(self, test_settings: Settings):
        """Test that settings are properly configured for integration tests."""
        assert test_settings.environment == "testing"
        assert test_settings.state_manager_secret == "test-secret-key"
        assert test_settings.mongo_uri is not None
        assert test_settings.mongo_database_name is not None

    def test_model_imports(self):
        """Test that all required models can be imported."""
        # Test that all models can be imported successfully
        from app.models.register_nodes_request import RegisterNodesRequestModel
        from app.models.graph_models import UpsertGraphTemplateRequest, NodeTemplate
        from app.models.create_models import CreateRequestModel, RequestStateModel
        from app.models.enqueue_request import EnqueueRequestModel
        from app.models.state_status_enum import StateStatusEnum
        
        # If we get here, all imports are successful
        assert True 