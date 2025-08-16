"""
Integration tests for the complete state-manager workflow.

These tests cover the full happy path:
1. Register nodes with the state-manager
2. Create a graph template with the registered nodes
3. Create states for the graph
4. Execute states and verify the workflow

Prerequisites:
- A running MongoDB instance
- A running Redis instance (if used by the system)
- The state-manager service running on localhost:8000
"""

import sys
import os
import pytest
import httpx    
from typing import List
import uuid

# Add the state-manager app to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.register_nodes_request import RegisterNodesRequestModel, NodeRegistrationModel
from app.models.graph_models import UpsertGraphTemplateRequest, NodeTemplate
from app.models.create_models import CreateRequestModel, RequestStateModel
from app.models.executed_models import ExecutedRequestModel
from app.models.enqueue_request import EnqueueRequestModel
from app.models.state_status_enum import StateStatusEnum

# Mark all tests as integration tests
pytestmark = pytest.mark.integration


class TestFullWorkflowIntegration:
    """Integration tests for the complete state-manager workflow."""
    
    @pytest.fixture
    async def state_manager_client(self):
        """Create an HTTP client for the state-manager."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            yield client
    
    @pytest.fixture
    def test_namespace(self) -> str:
        """Generate a unique test namespace."""
        return f"test-namespace-{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def test_api_key(self) -> str:
        """Get the test API key from environment."""
        return os.environ.get("TEST_API_KEY", "API-KEY")
    
    @pytest.fixture
    def test_graph_name(self) -> str:
        """Generate a unique test graph name."""
        return f"test-graph-{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def test_runtime_name(self) -> str:
        """Generate a unique test runtime name."""
        return f"test-runtime-{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def sample_node_registration(self) -> NodeRegistrationModel:
        """Create a sample node registration for testing."""
        return NodeRegistrationModel(
            name="TestNode",
            inputs_schema={
                "type": "object",
                "properties": {
                    "input1": {"type": "string"},
                    "input2": {"type": "number"}
                },
                "required": ["input1", "input2"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "output1": {"type": "string"},
                    "output2": {"type": "number"}
                }
            },
            secrets=["test_secret"]
        )
    
    @pytest.fixture
    def sample_graph_nodes(self, test_namespace: str) -> List[NodeTemplate]:
        """Create sample graph nodes for testing."""
        return [
            NodeTemplate(
                node_name="TestNode",
                namespace=test_namespace,
                identifier="node1",
                inputs={
                    "input1": "test_value",
                    "input2": 42
                },
                next_nodes=["node2"],
                unites=None
            ),
            NodeTemplate(
                node_name="TestNode",
                namespace=test_namespace,
                identifier="node2",
                inputs={
                    "input1": "{{node1.output1}}",
                    "input2": "{{node1.output2}}"
                },
                next_nodes=[],
                unites=None
            )
        ]
    
    async def test_register_nodes(self, state_manager_client, test_namespace: str, 
                                 test_api_key: str, test_runtime_name: str, 
                                 sample_node_registration: NodeRegistrationModel):
        """Test registering nodes with the state-manager."""
        
        # Prepare the request
        request_data = RegisterNodesRequestModel(
            runtime_name=test_runtime_name,
            nodes=[sample_node_registration]
        )
        
        # Make the request
        response = await state_manager_client.put(
            f"/v0/namespace/{test_namespace}/nodes/",
            json=request_data.model_dump(),
            headers={"X-API-Key": test_api_key}
        )
        
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert "runtime_name" in response_data
        assert response_data["runtime_name"] == test_runtime_name
        assert "registered_nodes" in response_data
        assert len(response_data["registered_nodes"]) == 1
        assert response_data["registered_nodes"][0]["name"] == "TestNode"
    
    async def test_upsert_graph_template(self, state_manager_client, test_namespace: str,
                                       test_api_key: str, test_graph_name: str,
                                       sample_graph_nodes: List[NodeTemplate]):
        """Test creating a graph template."""
        
        # Prepare the request
        request_data = UpsertGraphTemplateRequest(
            secrets={"test_secret": "secret_value"},
            nodes=sample_graph_nodes
        )
        
        # Make the request
        response = await state_manager_client.put(
            f"/v0/namespace/{test_namespace}/graph/{test_graph_name}",
            json=request_data.model_dump(),
            headers={"X-API-Key": test_api_key}
        )
        
        # Verify the response
        assert response.status_code == 201
        response_data = response.json()
        assert "nodes" in response_data
        assert "secrets" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
        assert "validation_status" in response_data
        assert len(response_data["nodes"]) == 2
    
    async def test_get_graph_template(self, state_manager_client, test_namespace: str,
                                    test_api_key: str, test_graph_name: str):
        """Test retrieving a graph template."""
        
        # Make the request
        response = await state_manager_client.get(
            f"/v0/namespace/{test_namespace}/graph/{test_graph_name}",
            headers={"X-API-Key": test_api_key}
        )
        
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert "nodes" in response_data
        assert "secrets" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
        assert "validation_status" in response_data
        assert len(response_data["nodes"]) == 2
    
    async def test_create_states(self, state_manager_client, test_namespace: str,
                               test_api_key: str, test_graph_name: str):
        """Test creating states for a graph."""
        
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
        
        # Make the request
        response = await state_manager_client.post(
            f"/v0/namespace/{test_namespace}/graph/{test_graph_name}/states/create",
            json=request_data.model_dump(),
            headers={"X-API-Key": test_api_key}
        )
        
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert "states" in response_data
        assert len(response_data["states"]) == 1
        
        # Store the state ID for later tests
        state_id = response_data["states"][0]["state_id"]
        return state_id
    
    async def test_queued_state(self, state_manager_client, test_namespace: str,
                                test_api_key: str):
        # Prepare the request
        request_data = EnqueueRequestModel(
            nodes=["TestNode"],
            batch_size=1
        )

        # Make the request
        response = await state_manager_client.post(
            f"/v0/namespace/{test_namespace}/states/enqueue",
            json=request_data.model_dump(),
            headers={"X-API-Key": test_api_key}
        )        
    
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert "namespace" in response_data 
        assert "count" in response_data
        assert "states" in response_data
        assert len(response_data["states"]) == 1
        assert response_data["states"][0]["node_name"] == "TestNode"
        assert response_data["states"][0]["identifier"] == "node1"
        assert response_data["states"][0]["inputs"] == {"input1": "test_value", "input2": 42}
    
    async def test_execute_state(self, state_manager_client, test_namespace: str,
                               test_api_key: str, state_id: str):
        """Test executing a state."""
        
        # Prepare the request
        request_data = ExecutedRequestModel(
            outputs=[
                {
                    "output1": "executed_value",
                    "output2": 100
                }
            ]
        )
        
        # Make the request
        response = await state_manager_client.post(
            f"/v0/namespace/{test_namespace}/states/{state_id}/executed",
            json=request_data.model_dump(),
            headers={"X-API-Key": test_api_key}
        )
        
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == StateStatusEnum.EXECUTED
    
    async def test_get_secrets(self, state_manager_client, test_namespace: str,
                             test_api_key: str, state_id: str):
        """Test retrieving secrets for a state."""
        
        # Make the request
        response = await state_manager_client.get(
            f"/v0/namespace/{test_namespace}/state/{state_id}/secrets",
            headers={"X-API-Key": test_api_key}
        )
        
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert "secrets" in response_data
        assert "test_secret" in response_data["secrets"]
        assert response_data["secrets"]["test_secret"] == "secret_value"
    
    async def test_full_workflow_happy_path(self, state_manager_client, test_namespace: str,
                                          test_api_key: str, test_graph_name: str,
                                          test_runtime_name: str, sample_node_registration: NodeRegistrationModel,
                                          sample_graph_nodes: List[NodeTemplate]):
        """Test the complete happy path workflow."""
        
        # Step 1: Register nodes
        await self.test_register_nodes(
            state_manager_client, test_namespace, test_api_key, 
            test_runtime_name, sample_node_registration
        )
        
        # Step 2: Create graph template
        await self.test_upsert_graph_template(
            state_manager_client, test_namespace, test_api_key,
            test_graph_name, sample_graph_nodes
        )
        
        # Step 3: Get graph template to verify it was created
        await self.test_get_graph_template(
            state_manager_client, test_namespace, test_api_key, test_graph_name
        )
        
        # Step 4: Create states
        state_id = await self.test_create_states(
            state_manager_client, test_namespace, test_api_key, test_graph_name
        )
        
        # Step 5: Get secrets for the state
        await self.test_get_secrets(
            state_manager_client, test_namespace, test_api_key, state_id
        )

        await self.test_queued_state(
            state_manager_client, test_namespace, test_api_key
        )
        
        # Step 6: Execute the state
        await self.test_execute_state(
            state_manager_client, test_namespace, test_api_key, state_id
        )
        
        # Step 7: Verify the complete workflow by checking the state was processed
        # This would typically involve checking the database or making additional API calls
        # to verify the state transitioned correctly through the workflow
        
        print(f"✅ Full workflow completed successfully for namespace: {test_namespace}")
        print(f"   - Graph: {test_graph_name}")
        print(f"   - State ID: {state_id}")
        print(f"   - Runtime: {test_runtime_name}")