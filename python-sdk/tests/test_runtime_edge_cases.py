import pytest
import asyncio
import warnings
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel
from exospherehost.runtime import Runtime, _setup_default_logging
from exospherehost.node.BaseNode import BaseNode


class MockTestNode(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        return self.Outputs(message=f"Hello {self.inputs.name}") # type: ignore


class MockTestNodeWithNonStringFields(BaseNode):
    class Inputs(BaseModel):
        name: str
        count: int  # This should cause validation error

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        return self.Outputs(message=f"Hello {self.inputs.name}") # type: ignore


class MockTestNodeWithoutSecrets(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        pass  # Empty secrets

    async def execute(self):
        return self.Outputs(message=f"Hello {self.inputs.name}") # type: ignore


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


class TestRuntimeEdgeCases:
    """Test edge cases and error handling scenarios in the Runtime class."""

    def test_setup_default_logging_disabled(self, monkeypatch):
        """Test that _setup_default_logging returns early when disabled."""
        monkeypatch.setenv('EXOSPHERE_DISABLE_DEFAULT_LOGGING', 'true')
        
        # This should not raise any exceptions and should return early
        _setup_default_logging()

    def test_setup_default_logging_invalid_level(self, monkeypatch):
        """Test _setup_default_logging with invalid log level."""
        monkeypatch.setenv('EXOSPHERE_LOG_LEVEL', 'INVALID_LEVEL')
        
        # Should fall back to INFO level
        _setup_default_logging()

    def test_runtime_validation_non_string_fields(self):
        """Test that Runtime validates node fields are strings."""
        with pytest.raises(ValueError, match="must be of type str"):
            Runtime(
                namespace="test",
                name="test",
                nodes=[MockTestNodeWithNonStringFields],
                state_manager_uri="http://localhost:8080",
                key="test_key"
            )

    def test_runtime_validation_duplicate_node_names(self):
        """Test that Runtime validates no duplicate node names."""
        # Create two classes with the same name
        class TestNode1(MockTestNode):
            pass
        
        class TestNode2(MockTestNode):
            pass
        
        # Rename the second class to have the same name as the first
        TestNode2.__name__ = "TestNode1"
        
        # Suppress the RuntimeWarning about unawaited coroutines
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*coroutine.*was never awaited.*", category=RuntimeWarning)
            with pytest.raises(ValueError, match="Duplicate node class names found"):
                Runtime(
                    namespace="test",
                    name="test",
                    nodes=[TestNode1, TestNode2],
                    state_manager_uri="http://localhost:8080",
                    key="test_key"
                )

    def test_need_secrets_empty_secrets(self):
        """Test _need_secrets with empty secrets class."""
        runtime = Runtime(
            namespace="test",
            name="test",
            nodes=[MockTestNodeWithoutSecrets],
            state_manager_uri="http://localhost:8080",
            key="test_key"
        )
        
        # Should return False for empty secrets
        assert not runtime._need_secrets(MockTestNodeWithoutSecrets)

    def test_need_secrets_with_secrets(self):
        """Test _need_secrets with secrets class that has fields."""
        runtime = Runtime(
            namespace="test",
            name="test",
            nodes=[MockTestNode],
            state_manager_uri="http://localhost:8080",
            key="test_key"
        )
        
        # Should return True for secrets with fields
        assert runtime._need_secrets(MockTestNode)

    @pytest.mark.asyncio
    async def test_enqueue_error_handling(self):
        """Test error handling in _enqueue method."""
        runtime = Runtime(
            namespace="test",
            name="test",
            nodes=[MockTestNode],
            state_manager_uri="http://localhost:8080",
            key="test_key"
        )
        
        # Mock _enqueue_call to raise an exception
        with patch.object(runtime, '_enqueue_call', side_effect=Exception("Test error")):
            # This should not raise an exception but log an error
            # We'll test this by checking that the method doesn't crash
            task = asyncio.create_task(runtime._enqueue())
            await asyncio.sleep(0.1)  # Let it run briefly
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def test_start_without_running_loop(self):
        """Test start method when no event loop is running."""
        runtime = Runtime(
            namespace="test",
            name="test",
            nodes=[MockTestNode],
            state_manager_uri="http://localhost:8080",
            key="test_key"
        )
        
        # Mock _start to avoid actual execution
        with patch.object(runtime, '_start', new_callable=AsyncMock):
            # This should not raise an exception
            result = runtime.start()
            assert result is None

    def test_start_with_running_loop(self):
        """Test start method when an event loop is already running."""
        runtime = Runtime(
            namespace="test",
            name="test",
            nodes=[MockTestNode],
            state_manager_uri="http://localhost:8080",
            key="test_key"
        )
        
        # Mock _start to avoid actual execution
        with patch.object(runtime, '_start', new_callable=AsyncMock):
            # Create a mock loop
            mock_loop = MagicMock()
            mock_task = MagicMock()
            mock_loop.create_task.return_value = mock_task
            
            with patch('asyncio.get_running_loop', return_value=mock_loop):
                result = runtime.start()
                assert result == mock_task 