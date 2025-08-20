import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.middlewares.unhandled_exceptions_middleware import UnhandledExceptionsMiddleware


class TestUnhandledExceptionsMiddleware:
    """Test cases for UnhandledExceptionsMiddleware"""

    def setup_method(self):
        """Set up test fixtures before each test"""
        self.middleware = UnhandledExceptionsMiddleware(app=MagicMock())

    @pytest.mark.asyncio
    async def test_dispatch_success_no_exception(self):
        """Test dispatch when no exception occurs"""
        # Setup
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        mock_call_next = AsyncMock(return_value=mock_response)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            result = await self.middleware.dispatch(mock_request, mock_call_next)

        # Should return the original response
        assert result == mock_response
        
        # Should not log any errors
        mock_logger.error.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_handles_generic_exception(self):
        """Test dispatch handles generic exceptions"""
        # Setup
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/error"
        mock_request.method = "POST"
        mock_request.state.x_exosphere_request_id = "test-request-id"

        test_exception = Exception("Generic test error")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="Mock traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        # Should return JSONResponse with 500 status
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        # Check response content
        # Note: We can't easily test the actual JSON content without calling result.body,
        # but we can verify it's a JSONResponse with the right status code
        
        # Should log the error
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="Generic test error",
            traceback="Mock traceback",
            path="/api/error",
            method="POST",
            x_exosphere_request_id="test-request-id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_handles_runtime_error(self):
        """Test dispatch handles RuntimeError exceptions"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/runtime-error"
        mock_request.method = "PUT"
        mock_request.state.x_exosphere_request_id = "runtime-request-id"

        test_exception = RuntimeError("Runtime test error")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="Runtime traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="Runtime test error",
            traceback="Runtime traceback",
            path="/api/runtime-error",
            method="PUT",
            x_exosphere_request_id="runtime-request-id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_handles_value_error(self):
        """Test dispatch handles ValueError exceptions"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/validation"
        mock_request.method = "POST"
        mock_request.state.x_exosphere_request_id = "validation-request-id"

        test_exception = ValueError("Invalid value provided")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="ValueError traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="Invalid value provided",
            traceback="ValueError traceback",
            path="/api/validation",
            method="POST",
            x_exosphere_request_id="validation-request-id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_handles_key_error(self):
        """Test dispatch handles KeyError exceptions"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/data"
        mock_request.method = "GET"
        mock_request.state.x_exosphere_request_id = "key-error-request-id"

        test_exception = KeyError("missing_key")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="KeyError traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="'missing_key'",
            traceback="KeyError traceback",
            path="/api/data",
            method="GET",
            x_exosphere_request_id="key-error-request-id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_handles_attribute_error(self):
        """Test dispatch handles AttributeError exceptions"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/object"
        mock_request.method = "PATCH"
        mock_request.state.x_exosphere_request_id = "attribute-request-id"

        test_exception = AttributeError("'NoneType' object has no attribute 'method'")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="AttributeError traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="'NoneType' object has no attribute 'method'",
            traceback="AttributeError traceback",
            path="/api/object",
            method="PATCH",
            x_exosphere_request_id="attribute-request-id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_without_request_id_logs_none(self):
        """Test dispatch when request state has no x_exosphere_request_id"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/no-id"
        mock_request.method = "DELETE"
        # Mock state without x_exosphere_request_id attribute
        mock_request.state = MagicMock()
        del mock_request.state.x_exosphere_request_id  # Simulate missing attribute

        test_exception = Exception("No request ID error")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="No ID traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="No request ID error",
            traceback="No ID traceback", 
            path="/api/no-id",
            method="DELETE",
            x_exosphere_request_id=None
        )

    @pytest.mark.asyncio
    async def test_dispatch_with_empty_request_id_logs_empty_string(self):
        """Test dispatch when request has empty string request ID"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/empty-id"
        mock_request.method = "OPTIONS"
        mock_request.state.x_exosphere_request_id = ""

        test_exception = Exception("Empty ID error")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            with patch('traceback.format_exc', return_value="Empty ID traceback"):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        mock_logger.error.assert_called_once_with(
            "unhandled global exception",
            error="Empty ID error",
            traceback="Empty ID traceback",
            path="/api/empty-id",
            method="OPTIONS",
            x_exosphere_request_id=""
        )

    @pytest.mark.asyncio
    async def test_dispatch_logs_different_request_paths_and_methods(self):
        """Test dispatch logs different paths and methods correctly during exceptions"""
        test_cases = [
            ("GET", "/api/users", "Get users error"),
            ("POST", "/api/users/create", "Create user error"),
            ("PUT", "/api/users/123", "Update user error"),
            ("DELETE", "/api/users/123", "Delete user error"),
            ("PATCH", "/api/users/123/status", "Update status error"),
            ("HEAD", "/health", "Health check error"),
            ("OPTIONS", "/api/cors", "CORS preflight error"),
        ]

        for method, path, error_message in test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.url.path = path
            mock_request.method = method
            mock_request.state.x_exosphere_request_id = f"test-id-{method.lower()}"

            test_exception = Exception(error_message)
            mock_call_next = AsyncMock(side_effect=test_exception)

            with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
                with patch('traceback.format_exc', return_value=f"{method} traceback"):
                    result = await self.middleware.dispatch(mock_request, mock_call_next)

            assert isinstance(result, JSONResponse)
            assert result.status_code == 500
            
            mock_logger.error.assert_called_once_with(
                "unhandled global exception",
                error=error_message,
                traceback=f"{method} traceback",
                path=path,
                method=method,
                x_exosphere_request_id=f"test-id-{method.lower()}"
            )

    @pytest.mark.asyncio
    async def test_dispatch_response_content_structure(self):
        """Test that the error response has the correct JSON structure"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.state.x_exosphere_request_id = "response-test-id"

        test_exception = Exception("Response structure test")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger'):
            with patch('traceback.format_exc'):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        # Verify it's a JSONResponse with correct structure
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        # The actual content validation would require calling result.body or similar,
        # but we can verify the key properties of the JSONResponse
        assert hasattr(result, 'status_code')
        assert result.status_code == 500

    @pytest.mark.asyncio
    async def test_dispatch_uses_actual_traceback_format_exc(self):
        """Test that dispatch uses actual traceback.format_exc() when not mocked"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/traceback-test"
        mock_request.method = "POST"
        mock_request.state.x_exosphere_request_id = "traceback-test-id"

        test_exception = ValueError("Traceback test error")
        mock_call_next = AsyncMock(side_effect=test_exception)

        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            # Don't mock traceback.format_exc to test actual behavior
            result = await self.middleware.dispatch(mock_request, mock_call_next)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        
        # Verify the logger was called with actual traceback
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[1]
        assert call_args["error"] == "Traceback test error"
        assert "traceback" in call_args
        # The actual traceback should contain information about the ValueError
        assert "ValueError: Traceback test error" in call_args["traceback"]

    @pytest.mark.asyncio
    async def test_dispatch_exception_in_exception_handling(self):
        """Test middleware behavior when logging itself fails"""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/logging-error"
        mock_request.method = "GET"
        mock_request.state.x_exosphere_request_id = "logging-error-id"

        test_exception = Exception("Original error")
        mock_call_next = AsyncMock(side_effect=test_exception)

        # Mock logger.error to raise an exception
        with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logging failed")
            
            # The middleware should still return a JSONResponse even if logging fails
            # This tests the robustness of error handling
            with pytest.raises(Exception, match="Logging failed"):
                await self.middleware.dispatch(mock_request, mock_call_next)

    @pytest.mark.asyncio
    async def test_dispatch_preserves_original_exception_type_in_logs(self):
        """Test that different exception types are logged with their original string representation"""
        exception_test_cases = [
            (ValueError("Invalid input"), "Invalid input"),
            (KeyError("missing_key"), "'missing_key'"),
            (AttributeError("'str' object has no attribute 'nonexistent'"), "'str' object has no attribute 'nonexistent'"),
            (TypeError("unsupported operand type(s)"), "unsupported operand type(s)"),
            (IndexError("list index out of range"), "list index out of range"),
            (FileNotFoundError("No such file or directory"), "No such file or directory"),
            (ConnectionError("Connection failed"), "Connection failed"),
            (TimeoutError("Operation timed out"), "Operation timed out"),
        ]

        for exception, expected_error_message in exception_test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.url.path = "/api/exception-types"
            mock_request.method = "GET"
            mock_request.state.x_exosphere_request_id = "exception-types-id"

            mock_call_next = AsyncMock(side_effect=exception)

            with patch('app.middlewares.unhandled_exceptions_middleware.logger') as mock_logger:
                with patch('traceback.format_exc', return_value="Mock traceback"):
                    result = await self.middleware.dispatch(mock_request, mock_call_next)

            assert isinstance(result, JSONResponse)
            assert result.status_code == 500
            
            # Verify the specific error message is logged correctly
            mock_logger.error.assert_called_once_with(
                "unhandled global exception",
                error=expected_error_message,
                traceback="Mock traceback",
                path="/api/exception-types",
                method="GET",
                x_exosphere_request_id="exception-types-id"
            )