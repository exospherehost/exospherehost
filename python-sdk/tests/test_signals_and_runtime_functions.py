import pytest
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta
from pydantic import BaseModel
from exospherehost.signals import PruneSignal, ReQueueAfterSignal
from exospherehost.runtime import Runtime, _setup_default_logging
from exospherehost.node.BaseNode import BaseNode


def create_mock_aiohttp_session():
    """Helper function to create a properly mocked aiohttp session."""
    mock_session = AsyncMock()
    
    # Create mock response objects
    mock_post_response = MagicMock()
    mock_get_response = MagicMock()
    mock_put_response = MagicMock()
    
    # Create mock context managers for each method
    mock_post_context = MagicMock()
    mock_post_context.__aenter__ = AsyncMock(return_value=mock_post_response)
    mock_post_context.__aexit__ = AsyncMock(return_value=None)
    
    mock_get_context = MagicMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_get_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    
    mock_put_context = MagicMock()
    mock_put_context.__aenter__ = AsyncMock(return_value=mock_put_response)
    mock_put_context.__aexit__ = AsyncMock(return_value=None)
    
    # Set up the session methods to return the context managers using MagicMock
    mock_session.post = MagicMock(return_value=mock_post_context)
    mock_session.get = MagicMock(return_value=mock_get_context)
    mock_session.put = MagicMock(return_value=mock_put_context)
    
    # Set up session context manager
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
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


class TestPruneSignal:
    """Test cases for PruneSignal exception class."""

    def test_prune_signal_initialization_with_data(self):
        """Test PruneSignal initialization with custom data."""
        data = {"reason": "test", "custom_field": "value"}
        signal = PruneSignal(data)
        
        assert signal.data == data
        assert "Prune signal received with data" in str(signal)
        assert "Do not catch this Exception" in str(signal)

    def test_prune_signal_initialization_without_data(self):
        """Test PruneSignal initialization without data (default empty dict)."""
        signal = PruneSignal()
        
        assert signal.data == {}
        assert "Prune signal received with data" in str(signal)

    def test_prune_signal_inheritance(self):
        """Test that PruneSignal properly inherits from Exception."""
        signal = PruneSignal()
        assert isinstance(signal, Exception)

    @pytest.mark.asyncio
    async def test_prune_signal_send_success(self):
        """Test successful sending of prune signal."""
        data = {"reason": "test_prune"}
        signal = PruneSignal(data)
        
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        
        with patch('exospherehost.signals.ClientSession', return_value=mock_session):
            await signal.send("http://test-endpoint/prune", "test-api-key")
        
        # Verify the request was made correctly
        mock_session.post.assert_called_once_with(
            "http://test-endpoint/prune",
            json=data,
            headers={"x-api-key": "test-api-key"}
        )

    @pytest.mark.asyncio
    async def test_prune_signal_send_failure(self):
        """Test prune signal sending failure."""
        data = {"reason": "test_prune"}
        signal = PruneSignal(data)
        
        class _FakeResponse:
            def __init__(self, status: int):
                self.status = status

        class _FakePostCtx:
            def __init__(self, status: int):
                self._status = status
            async def __aenter__(self):
                return _FakeResponse(self._status)
            async def __aexit__(self, exc_type, exc, tb):
                return None

        class _FakeSession:
            def __init__(self, status: int):
                self._status = status
            def post(self, *args, **kwargs):
                return _FakePostCtx(self._status)
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                return None

        with patch('exospherehost.signals.ClientSession', return_value=_FakeSession(500)):
            with pytest.raises(Exception, match="Failed to send prune signal"):
                await signal.send("http://test-endpoint/prune", "test-api-key")


class TestReQueueAfterSignal:
    """Test cases for ReQueueAfterSignal exception class."""

    def test_requeue_signal_initialization(self):
        """Test ReQueueAfterSignal initialization."""
        delta = timedelta(seconds=30)
        signal = ReQueueAfterSignal(delta)
        
        assert signal.delay == delta
        assert "ReQueueAfter signal received with timedelta" in str(signal)
        assert "Do not catch this Exception" in str(signal)

    def test_requeue_signal_inheritance(self):
        """Test that ReQueueAfterSignal properly inherits from Exception."""
        delta = timedelta(minutes=5)
        signal = ReQueueAfterSignal(delta)
        assert isinstance(signal, Exception)

    @pytest.mark.asyncio
    async def test_requeue_signal_send_success(self):
        """Test successful sending of requeue signal."""
        delta = timedelta(seconds=45)
        signal = ReQueueAfterSignal(delta)
        
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        
        with patch('exospherehost.signals.ClientSession', return_value=mock_session):
            await signal.send("http://test-endpoint/requeue", "test-api-key")
        
        # Verify the request was made correctly
        expected_body = {"enqueue_after": 45000}  # 45 seconds * 1000
        mock_session.post.assert_called_once_with(
            "http://test-endpoint/requeue",
            json=expected_body,
            headers={"x-api-key": "test-api-key"}
        )

    @pytest.mark.asyncio
    async def test_requeue_signal_send_with_minutes(self):
        """Test requeue signal sending with minutes in timedelta."""
        delta = timedelta(minutes=2, seconds=30)
        signal = ReQueueAfterSignal(delta)
        
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        
        with patch('exospherehost.signals.ClientSession', return_value=mock_session):
            await signal.send("http://test-endpoint/requeue", "test-api-key")
        
        # Verify the request was made correctly
        expected_body = {"enqueue_after": 150000}  # (2*60 + 30) seconds * 1000
        mock_session.post.assert_called_once_with(
            "http://test-endpoint/requeue",
            json=expected_body,
            headers={"x-api-key": "test-api-key"}
        )

    @pytest.mark.asyncio
    async def test_requeue_signal_send_failure(self):
        """Test requeue signal sending failure."""
        delta = timedelta(seconds=30)
        signal = ReQueueAfterSignal(delta)
        
        class _FakeResponse:
            def __init__(self, status: int):
                self.status = status

        class _FakePostCtx:
            def __init__(self, status: int):
                self._status = status
            async def __aenter__(self):
                return _FakeResponse(self._status)
            async def __aexit__(self, exc_type, exc, tb):
                return None

        class _FakeSession:
            def __init__(self, status: int):
                self._status = status
            def post(self, *args, **kwargs):
                return _FakePostCtx(self._status)
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                return None

        with patch('exospherehost.signals.ClientSession', return_value=_FakeSession(400)):
            with pytest.raises(Exception, match="Failed to send requeue after signal"):
                await signal.send("http://test-endpoint/requeue", "test-api-key")


class TestRuntimeSignalHandling:
    """Test cases for Runtime signal handling functionality."""

    def test_runtime_endpoint_construction(self):
        """Test that runtime constructs correct endpoints for signal handling."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Test prune endpoint construction
        prune_endpoint = runtime._get_prune_endpoint("test-state-id")
        expected_prune = "http://test-state-manager/v0/namespace/test-namespace/state/test-state-id/prune"
        assert prune_endpoint == expected_prune
        
        # Test requeue after endpoint construction
        requeue_endpoint = runtime._get_requeue_after_endpoint("test-state-id")
        expected_requeue = "http://test-state-manager/v0/namespace/test-namespace/state/test-state-id/re-enqueue-after"
        assert requeue_endpoint == expected_requeue

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore:.*coroutine.*was never awaited.*:RuntimeWarning")
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_signal_handling_direct(self):
        """Test signal handling by directly calling signal.send() with runtime endpoints."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Test PruneSignal with runtime endpoint
        prune_signal = PruneSignal({"reason": "direct_test"})
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        
        with patch('exospherehost.signals.ClientSession', return_value=mock_session):
            await prune_signal.send(runtime._get_prune_endpoint("test-state"), runtime._key) # type: ignore
        
        # Verify prune endpoint was called correctly
        mock_session.post.assert_called_once_with(
            runtime._get_prune_endpoint("test-state"),
            json={"reason": "direct_test"},
            headers={"x-api-key": "test-key"}
        )

    @pytest.mark.asyncio
    async def test_requeue_signal_handling_direct(self):
        """Test requeue signal handling by directly calling signal.send() with runtime endpoints."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Test ReQueueAfterSignal with runtime endpoint
        requeue_signal = ReQueueAfterSignal(timedelta(minutes=10))
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        
        with patch('exospherehost.signals.ClientSession', return_value=mock_session):
            await requeue_signal.send(runtime._get_requeue_after_endpoint("test-state"), runtime._key) # type: ignore
        
        # Verify requeue endpoint was called correctly
        expected_body = {"enqueue_after": 600000}  # 10 minutes * 60 * 1000
        mock_session.post.assert_called_once_with(
            runtime._get_requeue_after_endpoint("test-state"),
            json=expected_body,
            headers={"x-api-key": "test-key"}
        )

    def test_need_secrets_function(self):
        """Test the _need_secrets function."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Test with node that has secrets
        assert runtime._need_secrets(MockTestNode)
        
        # Test with node that has no secrets
        class MockNodeWithoutSecrets(BaseNode):
            class Inputs(BaseModel):
                name: str
            class Outputs(BaseModel):
                message: str
            class Secrets(BaseModel):
                pass
            async def execute(self):
                return self.Outputs(message="test")
        
        assert not runtime._need_secrets(MockNodeWithoutSecrets)

    @pytest.mark.asyncio
    async def test_get_secrets_function(self):
        """Test the _get_secrets function."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Mock successful secrets retrieval
        mock_session, _, mock_get_response, _ = create_mock_aiohttp_session()
        mock_get_response.status = 200
        mock_get_response.json = AsyncMock(return_value={"secrets": {"api_key": "test-secret"}})
        
        with patch('exospherehost.runtime.ClientSession', return_value=mock_session):
            secrets = await runtime._get_secrets("test-state-id")
        
        assert secrets == {"api_key": "test-secret"}
        mock_session.get.assert_called_once_with(
            runtime._get_secrets_endpoint("test-state-id"),
            headers={"x-api-key": "test-key"}
        )

    @pytest.mark.asyncio
    async def test_get_secrets_function_failure(self):
        """Test the _get_secrets function when request fails."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Mock failed secrets retrieval
        mock_session, _, mock_get_response, _ = create_mock_aiohttp_session()
        mock_get_response.status = 404
        mock_get_response.json = AsyncMock(return_value={"error": "Not found"})
        
        with patch('exospherehost.runtime.ClientSession', return_value=mock_session):
            secrets = await runtime._get_secrets("test-state-id")
        
        assert secrets == {}

    @pytest.mark.asyncio
    async def test_get_secrets_function_no_secrets_field(self):
        """Test the _get_secrets function when response has no secrets field."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Mock response without secrets field
        mock_session, _, mock_get_response, _ = create_mock_aiohttp_session()
        mock_get_response.status = 200
        mock_get_response.json = AsyncMock(return_value={"data": "some other data"})
        
        with patch('exospherehost.runtime.ClientSession', return_value=mock_session):
            secrets = await runtime._get_secrets("test-state-id")
        
        assert secrets == {}


class TestRuntimeEndpointFunctions:
    """Test cases for Runtime endpoint construction functions."""

    def test_get_prune_endpoint(self):
        """Test _get_prune_endpoint function."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        endpoint = runtime._get_prune_endpoint("state-123")
        expected = "http://test-state-manager/v0/namespace/test-namespace/state/state-123/prune"
        assert endpoint == expected

    def test_get_requeue_after_endpoint(self):
        """Test _get_requeue_after_endpoint function."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        endpoint = runtime._get_requeue_after_endpoint("state-456")
        expected = "http://test-state-manager/v0/namespace/test-namespace/state/state-456/re-enqueue-after"
        assert endpoint == expected

    def test_get_prune_endpoint_with_custom_version(self):
        """Test _get_prune_endpoint with custom state manager version."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key",
            state_manage_version="v1"
        )
        
        endpoint = runtime._get_prune_endpoint("state-789")
        expected = "http://test-state-manager/v1/namespace/test-namespace/state/state-789/prune"
        assert endpoint == expected

    def test_get_requeue_after_endpoint_with_custom_version(self):
        """Test _get_requeue_after_endpoint with custom state manager version."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key",
            state_manage_version="v2"
        )
        
        endpoint = runtime._get_requeue_after_endpoint("state-101")
        expected = "http://test-state-manager/v2/namespace/test-namespace/state/state-101/re-enqueue-after"
        assert endpoint == expected


class TestSignalIntegration:
    """Integration tests for signal handling in the runtime."""

    @pytest.mark.asyncio
    async def test_signal_exception_behavior(self):
        """Test that signals are proper exceptions that can be raised and caught."""
        # Test PruneSignal
        prune_signal = PruneSignal({"test": "data"})
        
        with pytest.raises(PruneSignal) as exc_info:
            raise prune_signal
        
        assert exc_info.value.data == {"test": "data"}
        assert isinstance(exc_info.value, Exception)
        
        # Test ReQueueAfterSignal
        requeue_signal = ReQueueAfterSignal(timedelta(seconds=30))
        
        with pytest.raises(ReQueueAfterSignal) as exc_info:
            raise requeue_signal
        
        assert exc_info.value.delay == timedelta(seconds=30)
        assert isinstance(exc_info.value, Exception)

    @pytest.mark.asyncio
    async def test_combined_signal_and_runtime_functionality(self):
        """Test that signals work correctly with runtime endpoints."""
        runtime = Runtime(
            namespace="production",
            name="signal-runtime",
            nodes=[MockTestNode],
            state_manager_uri="https://api.exosphere.host",
            key="prod-api-key",
            state_manage_version="v1"
        )
        
        # Test PruneSignal with production-like endpoint
        prune_signal = PruneSignal({"reason": "cleanup", "batch_id": "batch-123"})
        expected_prune_endpoint = "https://api.exosphere.host/v1/namespace/production/state/prod-state-456/prune"
        actual_prune_endpoint = runtime._get_prune_endpoint("prod-state-456")
        assert actual_prune_endpoint == expected_prune_endpoint
        
        # Test ReQueueAfterSignal with production-like endpoint
        requeue_signal = ReQueueAfterSignal(timedelta(hours=2, minutes=30))
        expected_requeue_endpoint = "https://api.exosphere.host/v1/namespace/production/state/prod-state-789/re-enqueue-after"
        actual_requeue_endpoint = runtime._get_requeue_after_endpoint("prod-state-789")
        assert actual_requeue_endpoint == expected_requeue_endpoint
        
        # Test that signal data is preserved
        assert prune_signal.data == {"reason": "cleanup", "batch_id": "batch-123"}
        assert requeue_signal.delay == timedelta(hours=2, minutes=30)

    @pytest.mark.asyncio
    async def test_signal_send_with_different_endpoints(self):
        """Test signal sending with various endpoint configurations."""
        # Test with different URI formats
        test_cases = [
            ("http://localhost:8080", "v0", "dev"),
            ("https://api.production.com", "v2", "production"),
            ("http://staging.internal:3000", "v1", "staging")
        ]
        
        for uri, version, namespace in test_cases:
            runtime = Runtime(
                namespace=namespace,
                name="test-runtime",
                nodes=[MockTestNode],
                state_manager_uri=uri,
                key="test-key",
                state_manage_version=version
            )
            
            # Test prune endpoint construction
            prune_endpoint = runtime._get_prune_endpoint("test-state")
            expected_prune = f"{uri}/{version}/namespace/{namespace}/state/test-state/prune"
            assert prune_endpoint == expected_prune
            
            # Test requeue endpoint construction
            requeue_endpoint = runtime._get_requeue_after_endpoint("test-state")
            expected_requeue = f"{uri}/{version}/namespace/{namespace}/state/test-state/re-enqueue-after"
            assert requeue_endpoint == expected_requeue


class TestSignalEdgeCases:
    """Test cases for signal edge cases and error conditions."""

    def test_prune_signal_with_empty_data(self):
        """Test PruneSignal with empty data."""
        signal = PruneSignal({})
        assert signal.data == {}
        assert isinstance(signal, Exception)

    def test_prune_signal_with_complex_data(self):
        """Test PruneSignal with complex nested data."""
        complex_data = {
            "reason": "batch_cleanup",
            "metadata": {
                "batch_id": "batch-456",
                "items": ["item1", "item2", "item3"],
                "timestamp": "2023-12-01T10:00:00Z"
            },
            "config": {
                "force": True,
                "notify_users": False
            }
        }
        signal = PruneSignal(complex_data)
        assert signal.data == complex_data

    def test_requeue_signal_with_zero_timedelta(self):
        """Test ReQueueAfterSignal with zero timedelta."""
        with pytest.raises(Exception):
            ReQueueAfterSignal(timedelta(seconds=0))

    def test_requeue_signal_with_large_timedelta(self):
        """Test ReQueueAfterSignal with large timedelta."""
        large_delta = timedelta(days=7, hours=12, minutes=30, seconds=45)
        signal = ReQueueAfterSignal(large_delta)
        assert signal.delay == large_delta

    @pytest.mark.asyncio
    async def test_requeue_signal_timedelta_conversion(self):
        """Test that ReQueueAfterSignal correctly converts timedelta to milliseconds."""
        test_cases = [
            (timedelta(seconds=1), 1000),
            (timedelta(minutes=1), 60000),
            (timedelta(hours=1), 3600000),
            (timedelta(days=1), 86400000),
            (timedelta(seconds=30, microseconds=500000), 30500),  # 30.5 seconds
        ]
        
        for delta, expected_ms in test_cases:
            signal = ReQueueAfterSignal(delta)
            
            mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
            mock_post_response.status = 200
            
            with patch('exospherehost.signals.ClientSession', return_value=mock_session):
                await signal.send("http://test-endpoint", "test-key")
            
            # Verify correct milliseconds conversion
            expected_body = {"enqueue_after": expected_ms}
            mock_session.post.assert_called_with(
                "http://test-endpoint",
                json=expected_body,
                headers={"x-api-key": "test-key"}
            )

    def test_signal_string_representations(self):
        """Test string representations of signals."""
        prune_signal = PruneSignal({"test": "data"})
        prune_str = str(prune_signal)
        assert "Prune signal received with data" in prune_str
        assert "Do not catch this Exception" in prune_str
        assert "{'test': 'data'}" in prune_str
        
        requeue_signal = ReQueueAfterSignal(timedelta(minutes=5))
        requeue_str = str(requeue_signal)
        assert "ReQueueAfter signal received with timedelta" in requeue_str
        assert "Do not catch this Exception" in requeue_str

class TestRuntimeHelperFunctions:
    """Test cases for Runtime helper functions."""

    @pytest.mark.asyncio
    async def test_notify_executed_function(self):
        """Test the _notify_executed function."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Mock successful notification
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        mock_post_response.json = AsyncMock(return_value={"status": "success"})
        
        # Create test outputs
        outputs = [MockTestNode.Outputs(message="output1"), MockTestNode.Outputs(message="output2")]
        
        with patch('exospherehost.runtime.ClientSession', return_value=mock_session):
            await runtime._notify_executed("test-state-id", outputs) # type: ignore
        
        # Verify correct endpoint and payload
        expected_body = {"outputs": [{"message": "output1"}, {"message": "output2"}]}
        mock_session.post.assert_called_once_with(
            runtime._get_executed_endpoint("test-state-id"),
            json=expected_body,
            headers={"x-api-key": "test-key"}
        )

    @pytest.mark.asyncio
    async def test_notify_errored_function(self):
        """Test the _notify_errored function."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Mock successful notification
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 200
        mock_post_response.json = AsyncMock(return_value={"status": "success"})
        
        with patch('exospherehost.runtime.ClientSession', return_value=mock_session):
            await runtime._notify_errored("test-state-id", "Test error message")
        
        # Verify correct endpoint and payload
        expected_body = {"error": "Test error message"}
        mock_session.post.assert_called_once_with(
            runtime._get_errored_endpoint("test-state-id"),
            json=expected_body,
            headers={"x-api-key": "test-key"}
        )

    @pytest.mark.asyncio
    async def test_notify_functions_with_failure(self):
        """Test notification functions when HTTP requests fail."""
        runtime = Runtime(
            namespace="test-namespace",
            name="test-runtime",
            nodes=[MockTestNode],
            state_manager_uri="http://test-state-manager",
            key="test-key"
        )
        
        # Mock failed notification
        mock_session, mock_post_response, _, _ = create_mock_aiohttp_session()
        mock_post_response.status = 500
        mock_post_response.json = AsyncMock(return_value={"error": "Internal server error"})
        
        outputs = [MockTestNode.Outputs(message="test")]
        
        with patch('exospherehost.runtime.ClientSession', return_value=mock_session):
            # These should not raise exceptions, just log errors
            await runtime._notify_executed("test-state-id", outputs) # type: ignore
            await runtime._notify_errored("test-state-id", "Test error")
        
        # Verify both endpoints were called despite failures
        assert mock_session.post.call_count == 2


class TestSetupDefaultLogging:
    """Test cases for the _setup_default_logging function."""

    def test_setup_default_logging_with_existing_handlers(self):
        """Test that _setup_default_logging doesn't interfere with existing handlers."""
        # Create a logger with existing handlers
        test_logger = logging.getLogger("test_logger")
        handler = logging.StreamHandler()
        test_logger.addHandler(handler)
        
        # Mock the root logger to have handlers
        with patch('logging.getLogger') as mock_get_logger:
            mock_root_logger = MagicMock()
            mock_root_logger.handlers = [handler]
            mock_get_logger.return_value = mock_root_logger
            
            # This should return early and not configure logging
            _setup_default_logging()
            
            # Verify no basic config was called
            mock_root_logger.basicConfig = MagicMock()
            assert not mock_root_logger.basicConfig.called

    def test_setup_default_logging_with_disable_env_var(self):
        """Test that _setup_default_logging respects the disable environment variable."""
        with patch.dict('os.environ', {'EXOSPHERE_DISABLE_DEFAULT_LOGGING': 'true'}), \
             patch('logging.getLogger') as mock_get_logger:
            mock_root_logger = MagicMock()
            mock_root_logger.handlers = []
            mock_get_logger.return_value = mock_root_logger
            
            _setup_default_logging()
            
            # Should return early due to env var
            with patch('logging.basicConfig') as mock_basic_config:
                _setup_default_logging()
                assert not mock_basic_config.called

    def test_setup_default_logging_with_custom_log_level(self):
        """Test that _setup_default_logging respects custom log level."""
        with patch.dict('os.environ', {'EXOSPHERE_LOG_LEVEL': 'DEBUG'}), \
             patch('logging.getLogger') as mock_get_logger, \
             patch('logging.basicConfig') as mock_basic_config:
            
            mock_root_logger = MagicMock()
            mock_root_logger.handlers = []
            mock_get_logger.return_value = mock_root_logger
            
            _setup_default_logging()
            
            # Verify basicConfig was called with DEBUG level
            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == logging.DEBUG 