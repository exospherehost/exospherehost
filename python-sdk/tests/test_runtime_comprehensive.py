import pytest
import asyncio
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel
from exospherehost.runtime import Runtime, _setup_default_logging
from exospherehost.node.BaseNode import BaseNode


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


class MockTestNode(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        return self.Outputs(message=f"Hello {self.inputs.name}") # type: ignore


class MockTestNodeWithListOutput(BaseNode):
    class Inputs(BaseModel):
        count: str

    class Outputs(BaseModel):
        numbers: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        count = int(self.inputs.count) # type: ignore
        return [self.Outputs(numbers=str(i)) for i in range(count)]


class MockTestNodeWithError(BaseNode):
    class Inputs(BaseModel):
        should_fail: str

    class Outputs(BaseModel):
        result: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        if self.inputs.should_fail == "true": # type: ignore
            raise ValueError("Test error")
        return self.Outputs(result="success")


class MockTestNodeWithNoneOutput(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        return None


@pytest.fixture
def runtime_config():
    return {
        "namespace": "test_namespace",
        "name": "test_runtime",
        "nodes": [MockTestNode],
        "state_manager_uri": "http://localhost:8080",
        "key": "test_key",
        "batch_size": 5,
        "workers": 2,
        "state_manage_version": "v1",
        "poll_interval": 1
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://localhost:8080")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "test_key")


class TestRuntimeInitialization:
    def test_runtime_initialization_with_all_params(self, runtime_config):
        runtime = Runtime(**runtime_config)
        assert runtime._namespace == "test_namespace"
        assert runtime._name == "test_runtime"
        assert runtime._key == "test_key"
        assert runtime._batch_size == 5
        assert runtime._workers == 2
        assert runtime._state_manager_version == "v1"
        assert runtime._poll_interval == 1
        assert MockTestNode in runtime._nodes
        assert "MockTestNode" in runtime._node_names

    def test_runtime_initialization_with_env_vars(self, mock_env_vars):
        runtime = Runtime(
            namespace="test_namespace",
            name="test_runtime",
            nodes=[MockTestNode]
        )
        assert runtime._state_manager_uri == "http://localhost:8080"
        assert runtime._key == "test_key"

    def test_runtime_validation_batch_size_less_than_one(self, mock_env_vars):
        with pytest.raises(ValueError, match="Batch size should be at least 1"):
            Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[MockTestNode],
                batch_size=0
            )

    def test_runtime_validation_workers_less_than_one(self, mock_env_vars):
        with pytest.raises(ValueError, match="Workers should be at least 1"):
            Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[MockTestNode],
                workers=0
            )

    def test_runtime_validation_missing_uri(self, monkeypatch):
        monkeypatch.delenv("EXOSPHERE_STATE_MANAGER_URI", raising=False)
        monkeypatch.setenv("EXOSPHERE_API_KEY", "test_key")
        with pytest.raises(ValueError, match="State manager URI is not set"):
            Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[MockTestNode]
            )

    def test_runtime_validation_missing_key(self, monkeypatch):
        monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://localhost:8080")
        monkeypatch.delenv("EXOSPHERE_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is not set"):
            Runtime(
                namespace="test_namespace",
                name="test_runtime",
                nodes=[MockTestNode]
            )


class TestRuntimeEndpointConstruction:
    def test_get_enque_endpoint(self, runtime_config):
        runtime = Runtime(**runtime_config)
        endpoint = runtime._get_enque_endpoint()
        expected = "http://localhost:8080/v1/namespace/test_namespace/states/enqueue"
        assert endpoint == expected

    def test_get_executed_endpoint(self, runtime_config):
        runtime = Runtime(**runtime_config)
        endpoint = runtime._get_executed_endpoint("state123")
        expected = "http://localhost:8080/v1/namespace/test_namespace/states/state123/executed"
        assert endpoint == expected

    def test_get_errored_endpoint(self, runtime_config):
        runtime = Runtime(**runtime_config)
        endpoint = runtime._get_errored_endpoint("state123")
        expected = "http://localhost:8080/v1/namespace/test_namespace/states/state123/errored"
        assert endpoint == expected

    def test_get_register_endpoint(self, runtime_config):
        runtime = Runtime(**runtime_config)
        endpoint = runtime._get_register_endpoint()
        expected = "http://localhost:8080/v1/namespace/test_namespace/nodes/"
        assert endpoint == expected

    def test_get_secrets_endpoint(self, runtime_config):
        runtime = Runtime(**runtime_config)
        endpoint = runtime._get_secrets_endpoint("state123")
        expected = "http://localhost:8080/v1/namespace/test_namespace/state/state123/secrets"
        assert endpoint == expected


class TestRuntimeRegistration:
    @pytest.mark.asyncio
    async def test_register_success(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={"status": "success"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            result = await runtime._register()
            
            assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_register_failure(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 400
            mock_put_response.json = AsyncMock(return_value={"error": "Bad request"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            with pytest.raises(RuntimeError, match="Failed to register nodes"):
                await runtime._register()


class TestRuntimeEnqueue:
    @pytest.mark.asyncio
    async def test_enqueue_call_success(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"states": [{"state_id": "1", "node_name": "MockTestNode", "inputs": {"name": "test"}}]})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            result = await runtime._enqueue_call()
            
            assert result == {"states": [{"state_id": "1", "node_name": "MockTestNode", "inputs": {"name": "test"}}]}

    @pytest.mark.asyncio
    async def test_enqueue_call_failure(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 500
            mock_post_response.json = AsyncMock(return_value={"error": "Internal server error"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            with pytest.raises(RuntimeError, match="Failed to enqueue states"):
                await runtime._enqueue_call()


class TestRuntimeWorker:
    @pytest.mark.asyncio
    async def test_worker_successful_execution(self, runtime_config):
        with patch('exospherehost.runtime.Runtime._get_secrets') as mock_get_secrets, \
             patch('exospherehost.runtime.Runtime._notify_executed') as mock_notify_executed:
            
            mock_get_secrets.return_value = {"api_key": "test_key"}
            mock_notify_executed.return_value = None
            
            runtime = Runtime(**runtime_config)
            
            # Create a test state
            state = {
                "state_id": "test_state_1",
                "node_name": "MockTestNode",
                "inputs": {"name": "test_user"}
            }
            
            # Put state in queue
            await runtime._state_queue.put(state)
            
            # Run worker for one iteration
            worker_task = asyncio.create_task(runtime._worker(1))
            
            # Wait a bit for processing
            await asyncio.sleep(0.1)
            
            # Cancel the worker
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
            
            # Verify secrets were fetched
            mock_get_secrets.assert_called_once_with("test_state_1")
            
            # Verify execution was notified
            mock_notify_executed.assert_called_once()
            call_args = mock_notify_executed.call_args
            assert call_args[0][0] == "test_state_1"  # state_id
            assert len(call_args[0][1]) == 1  # outputs list
            assert call_args[0][1][0].message == "Hello test_user"

    @pytest.mark.asyncio
    async def test_worker_with_list_output(self, runtime_config):
        runtime_config["nodes"] = [MockTestNodeWithListOutput]
        
        with patch('exospherehost.runtime.Runtime._get_secrets') as mock_get_secrets, \
             patch('exospherehost.runtime.Runtime._notify_executed') as mock_notify_executed:
            
            mock_get_secrets.return_value = {"api_key": "test_key"}
            mock_notify_executed.return_value = None
            
            runtime = Runtime(**runtime_config)
            
            state = {
                "state_id": "test_state_1",
                "node_name": "MockTestNodeWithListOutput",
                "inputs": {"count": "3"}
            }
            
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
            
            mock_notify_executed.assert_called_once()
            call_args = mock_notify_executed.call_args
            assert len(call_args[0][1]) == 3  # 3 outputs
            assert call_args[0][1][0].numbers == "0"
            assert call_args[0][1][1].numbers == "1"
            assert call_args[0][1][2].numbers == "2"

    @pytest.mark.asyncio
    async def test_worker_with_none_output(self, runtime_config):
        runtime_config["nodes"] = [MockTestNodeWithNoneOutput]
        
        with patch('exospherehost.runtime.Runtime._get_secrets') as mock_get_secrets, \
             patch('exospherehost.runtime.Runtime._notify_executed') as mock_notify_executed:
            
            mock_get_secrets.return_value = {"api_key": "test_key"}
            mock_notify_executed.return_value = None
            
            runtime = Runtime(**runtime_config)
            
            state = {
                "state_id": "test_state_1",
                "node_name": "MockTestNodeWithNoneOutput",
                "inputs": {"name": "test"}
            }
            
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
            
            mock_notify_executed.assert_called_once()
            call_args = mock_notify_executed.call_args
            assert call_args[0][1] == []  # Empty list for None output

    @pytest.mark.asyncio
    async def test_worker_execution_error(self, runtime_config):
        runtime_config["nodes"] = [MockTestNodeWithError]
        
        with patch('exospherehost.runtime.Runtime._get_secrets') as mock_get_secrets, \
             patch('exospherehost.runtime.Runtime._notify_errored') as mock_notify_errored:
            
            mock_get_secrets.return_value = {"api_key": "test_key"}
            mock_notify_errored.return_value = None
            
            runtime = Runtime(**runtime_config)
            
            state = {
                "state_id": "test_state_1",
                "node_name": "MockTestNodeWithError",
                "inputs": {"should_fail": "true"}
            }
            
            await runtime._state_queue.put(state)
            
            worker_task = asyncio.create_task(runtime._worker(1))
            await asyncio.sleep(0.1)
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
            
            mock_notify_errored.assert_called_once()
            call_args = mock_notify_errored.call_args
            assert call_args[0][0] == "test_state_1"  # state_id
            assert "Test error" in call_args[0][1]  # error message


class TestRuntimeNotification:
    @pytest.mark.asyncio
    async def test_notify_executed_success(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"status": "success"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            # Add the state_id to the node mapping
            runtime._node_mapping["test_state_1"] = MockTestNode
            outputs = [MockTestNode.Outputs(message="test output")]
            
            await runtime._notify_executed("test_state_1", outputs) # type: ignore
            
            # Verify the call was made
            mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_executed_failure(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 400
            mock_post_response.json = AsyncMock(return_value={"error": "Bad request"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            # Add the state_id to the node mapping
            runtime._node_mapping["test_state_1"] = MockTestNode
            outputs = [MockTestNode.Outputs(message="test output")]
            
            # Should not raise exception, just log error
            await runtime._notify_executed("test_state_1", outputs) # type: ignore

    @pytest.mark.asyncio
    async def test_notify_errored_success(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"status": "success"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            # Add the state_id to the node mapping
            runtime._node_mapping["test_state_1"] = MockTestNode
            
            await runtime._notify_errored("test_state_1", "Test error message")
            
            # Verify the call was made
            mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_errored_failure(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 400
            mock_post_response.json = AsyncMock(return_value={"error": "Bad request"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            # Add the state_id to the node mapping
            runtime._node_mapping["test_state_1"] = MockTestNode
            
            # Should not raise exception, just log error
            await runtime._notify_errored("test_state_1", "Test error message")


class TestRuntimeSecrets:
    @pytest.mark.asyncio
    async def test_get_secrets_success(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "secret_key"}})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            result = await runtime._get_secrets("test_state_1")
            
            assert result == {"api_key": "secret_key"}

    @pytest.mark.asyncio
    async def test_get_secrets_failure(self, runtime_config):
        with patch('exospherehost.runtime.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_get_response.status = 404
            mock_get_response.json = AsyncMock(return_value={"error": "Not found"})
            
            mock_session_class.return_value = mock_session
            
            runtime = Runtime(**runtime_config)
            result = await runtime._get_secrets("test_state_1")
            
            # Should return empty dict on failure
            assert result == {}


class TestRuntimeStart:
    @pytest.mark.asyncio
    async def test_start_with_existing_loop(self, runtime_config):
        with patch('exospherehost.runtime.Runtime._register') as mock_register, \
             patch('exospherehost.runtime.Runtime._enqueue') as mock_enqueue, \
             patch('exospherehost.runtime.Runtime._worker') as mock_worker:
            
            mock_register.return_value = None
            mock_enqueue.return_value = None
            mock_worker.return_value = None
            
            runtime = Runtime(**runtime_config)
            
            # Create a task in existing event loop
            task = runtime.start()
            
            assert isinstance(task, asyncio.Task)
            
            # Cancel the task
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def test_start_without_loop(self, runtime_config):
        with patch('exospherehost.runtime.Runtime._register') as mock_register, \
             patch('exospherehost.runtime.Runtime._enqueue') as mock_enqueue, \
             patch('exospherehost.runtime.Runtime._worker') as mock_worker:
            
            mock_register.return_value = None
            mock_enqueue.return_value = None
            mock_worker.return_value = None
            
            Runtime(**runtime_config)
            
            # This should not raise an exception
            # Note: In a real scenario, this would run the event loop
            # but we're mocking the async methods to avoid that


class TestLoggingSetup:
    def test_setup_default_logging_with_existing_handlers(self):
        # Test that it doesn't interfere with existing logging
        logger = logging.getLogger()
        original_handlers = logger.handlers.copy()
        
        _setup_default_logging()
        
        # Should not add new handlers if they already exist
        assert logger.handlers == original_handlers

    def test_setup_default_logging_with_env_disable(self, monkeypatch):
        monkeypatch.setenv('EXOSPHERE_DISABLE_DEFAULT_LOGGING', '1')
        
        # Clear existing handlers
        logger = logging.getLogger()
        original_handlers = logger.handlers.copy()
        
        _setup_default_logging()
        
        # Should not add handlers when disabled
        assert logger.handlers == original_handlers

    def test_setup_default_logging_with_custom_level(self, monkeypatch):
        monkeypatch.setenv('EXOSPHERE_LOG_LEVEL', 'DEBUG')
        
        # Clear existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        _setup_default_logging()
        
        # Should set up logging with custom level
        assert len(logger.handlers) > 0 