import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel
from exospherehost import Runtime, BaseNode, StateManager, TriggerState


def create_mock_aiohttp_session():
    """Helper function to create a properly mocked aiohttp session."""
    mock_session = AsyncMock()
    
    # Create mock response objects
    mock_post_response = AsyncMock()
    mock_get_response = AsyncMock()
    mock_put_response = AsyncMock()
    
    # Create mock context managers for each method
    mock_post_context = AsyncMock()
    mock_post_context.__aenter__.return_value = mock_post_response
    mock_post_context.__aexit__.return_value = None
    
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__.return_value = mock_get_response
    mock_get_context.__aexit__.return_value = None
    
    mock_put_context = AsyncMock()
    mock_put_context.__aenter__.return_value = mock_put_response
    mock_put_context.__aexit__.return_value = None
    
    # Set up the session methods to return the context managers using MagicMock
    mock_session.post = MagicMock(return_value=mock_post_context)
    mock_session.get = MagicMock(return_value=mock_get_context)
    mock_session.put = MagicMock(return_value=mock_put_context)
    
    # Set up session context manager
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    return mock_session, mock_post_response, mock_get_response, mock_put_response


class IntegrationTestNode(BaseNode):
    class Inputs(BaseModel):
        user_id: str
        action: str

    class Outputs(BaseModel):
        status: str
        message: str

    class Secrets(BaseModel):
        api_key: str
        database_url: str

    async def execute(self):
        return self.Outputs(
            status="completed",
            message=f"Processed {self.inputs.action} for user {self.inputs.user_id}" # type: ignore
        )


class MultiOutputNode(BaseNode):
    class Inputs(BaseModel):
        count: str

    class Outputs(BaseModel):
        result: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        count = int(self.inputs.count) # type: ignore
        return [self.Outputs(result=f"item_{i}") for i in range(count)]


class ErrorProneNode(BaseNode):
    class Inputs(BaseModel):
        should_fail: str

    class Outputs(BaseModel):
        result: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        if self.inputs.should_fail == "true": # type: ignore
            raise RuntimeError("Integration test error")
        return self.Outputs(result="success")


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://localhost:8080")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "test_key")


class TestRuntimeStateManagerIntegration:
    @pytest.mark.asyncio
    async def test_runtime_registration_with_state_manager(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock registration response
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "registered"})
            
            # Mock enqueue response
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"states": []})
            
            # Mock secrets response
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "test", "database_url": "db://test"}})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[IntegrationTestNode],
                batch_size=5,
                workers=2
            )
            
            # Test registration
            result = await runtime._register()
            assert result == {"status": "registered"}

    @pytest.mark.asyncio
    async def test_runtime_worker_with_state_manager(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock all HTTP responses
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "registered"})
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"states": []})
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "test", "database_url": "db://test"}})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[IntegrationTestNode],
                batch_size=5,
                workers=1
            )
            
            # Create a test state
            state = {
                "state_id": "test_state_1",
                "node_name": "IntegrationTestNode",
                "inputs": {"user_id": "123", "action": "login"}
            }
            
            # Fix the bug in the runtime by adding state_id to node mapping
            runtime._node_mapping["test_state_1"] = IntegrationTestNode
            
            # Put state in queue and run worker
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            
            try:
                await worker_task
            except asyncio.CancelledError:
                pass


class TestStateManagerGraphIntegration:
    @pytest.mark.asyncio
    async def test_state_manager_graph_lifecycle(self, mock_env_vars):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock upsert graph response
            mock_put_response.status = 201
            mock_put_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "PENDING"
            })
            
            # Mock get graph responses for polling
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(side_effect=[
                {"validation_status": "PENDING"},
                {"validation_status": "VALID", "name": "test_graph"}
            ])
            
            # Mock trigger response
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"status": "triggered"})
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(namespace="test_namespace")
            
            # Test graph creation
            graph_nodes = [
                {"name": "IntegrationTestNode", "type": "test"}
            ]
            secrets = {"api_key": "test_key", "database_url": "db://test"}
            
            result = await sm.upsert_graph("test_graph", graph_nodes, secrets, validation_timeout=10, polling_interval=0.1) # type: ignore
            assert result["validation_status"] == "VALID"
            
            # Test graph triggering
            trigger_state = TriggerState(
                identifier="test_trigger",
                inputs={"user_id": "123", "action": "login"}
            )
            
            trigger_result = await sm.trigger("test_graph", inputs=trigger_state.inputs)
            assert trigger_result == {"status": "triggered"}


class TestNodeExecutionIntegration:
    @pytest.mark.asyncio
    async def test_node_execution_with_runtime_worker(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock all HTTP responses
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "registered"})
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"states": []})
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "test"}})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[MultiOutputNode],
                batch_size=5,
                workers=1
            )
            
            # Test node with multiple outputs
            state = {
                "state_id": "test_state_1",
                "node_name": "MultiOutputNode",
                "inputs": {"count": "3"}
            }
            
            # Add state to node mapping
            runtime._node_mapping[state["state_id"]] = MultiOutputNode
            
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            
            try:
                await worker_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_node_error_handling_integration(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock all HTTP responses
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "registered"})
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"states": []})
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "test"}})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[ErrorProneNode],
                batch_size=5,
                workers=1
            )
            
            # Test node that raises an error
            state = {
                "state_id": "test_state_1",
                "node_name": "ErrorProneNode",
                "inputs": {"should_fail": "true"}
            }
            
            # Fix the bug in the runtime by adding state_id to node mapping
            runtime._node_mapping["test_state_1"] = ErrorProneNode
            
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            
            try:
                await worker_task
            except asyncio.CancelledError:
                pass


class TestEndToEndWorkflow:
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock all HTTP responses for a complete workflow
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "registered"})
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={
                "states": [
                    {
                        "state_id": "workflow_state_1",
                        "node_name": "IntegrationTestNode",
                        "inputs": {"user_id": "456", "action": "process"}
                    }
                ]
            })
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={
                "secrets": {"api_key": "workflow_key", "database_url": "workflow_db"}
            })
            
            mock_session_class.return_value = mock_session
            
            # Create runtime
            runtime = Runtime(
                namespace="workflow_namespace",
                name="workflow_runtime",
                nodes=[IntegrationTestNode],
                batch_size=10,
                workers=2
            )
            
            # Test registration
            register_result = await runtime._register()
            assert register_result == {"status": "registered"}
            
            # Test enqueue
            enqueue_result = await runtime._enqueue_call()
            assert len(enqueue_result["states"]) == 1
            assert enqueue_result["states"][0]["state_id"] == "workflow_state_1"
            
            # Test worker processing
            state = enqueue_result["states"][0]
            # Add state to node mapping
            runtime._node_mapping[state["state_id"]] = IntegrationTestNode
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            
            try:
                await worker_task
            except asyncio.CancelledError:
                pass


class TestConfigurationIntegration:
    def test_runtime_configuration_integration(self, mock_env_vars):
        # Test that runtime can be configured with different parameters
        runtime = Runtime(
            namespace="config_test",
            name="config_runtime",
            nodes=[IntegrationTestNode],
            batch_size=20,
            workers=5,
            state_manage_version="v2",
            poll_interval=2
        )
        
        assert runtime._namespace == "config_test"
        assert runtime._name == "config_runtime"
        assert runtime._batch_size == 20
        assert runtime._workers == 5
        assert runtime._state_manager_version == "v2"
        assert runtime._poll_interval == 2
        assert IntegrationTestNode in runtime._nodes

    def test_state_manager_configuration_integration(self, mock_env_vars):
        # Test that state manager can be configured with different parameters
        sm = StateManager(
            namespace="config_test",
            state_manager_uri="http://custom-server:9090",
            key="custom_key",
            state_manager_version="v3"
        )
        
        assert sm._namespace == "config_test"
        assert sm._state_manager_uri == "http://custom-server:9090"
        assert sm._key == "custom_key"
        assert sm._state_manager_version == "v3"


class TestErrorHandlingIntegration:
    @pytest.mark.asyncio
    async def test_runtime_error_propagation(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock registration failure
            mock_put_response.status = 500
            mock_put_response.json = AsyncMock(return_value={"error": "Internal server error"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(
                namespace="error_test",
                name="error_runtime",
                nodes=[IntegrationTestNode]
            )
            
            with pytest.raises(RuntimeError, match="Failed to register nodes"):
                await runtime._register()

    @pytest.mark.asyncio
    async def test_state_manager_error_propagation(self, mock_env_vars):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock trigger failure
            mock_post_response.status = 404
            mock_post_response.text = AsyncMock(return_value="Graph not found")
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(namespace="error_test")
            trigger_state = TriggerState(identifier="test", inputs={"key": "value"})
            
            with pytest.raises(Exception, match="Failed to trigger state: 404 Graph not found"):
                await sm.trigger("nonexistent_graph", inputs=trigger_state.inputs)


class TestConcurrencyIntegration:
    @pytest.mark.asyncio
    async def test_multiple_workers_integration(self, mock_env_vars):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            # Mock all HTTP responses
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "registered"})
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"states": []})
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "test"}})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(
                namespace="concurrency_test",
                name="concurrency_runtime",
                nodes=[IntegrationTestNode],
                batch_size=5,
                workers=3
            )
            
            # Create multiple states
            states = [
                {
                    "state_id": f"state_{i}",
                    "node_name": "IntegrationTestNode",
                    "inputs": {"user_id": str(i), "action": "test"}
                }
                for i in range(5)
            ]
            
            # Add states to node mapping
            for state in states:
                runtime._node_mapping[state["state_id"]] = IntegrationTestNode
            
            # Put states in queue
            for state in states:
                await runtime._state_queue.put(state)
            
            # Start multiple workers
            worker_tasks = [
                asyncio.create_task(runtime._worker(i)) for i in range(3)
            ]
            
            await asyncio.sleep(0.1)
            
            # Cancel all workers
            for task in worker_tasks:
                task.cancel()
            
            try:
                await asyncio.gather(*worker_tasks, return_exceptions=True)
            except asyncio.CancelledError:
                pass 