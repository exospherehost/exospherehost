import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.requests import Request
from starlette.responses import Response

from app.middlewares.request_id_middleware import RequestIdMiddleware


class TestRequestIdMiddleware:
    """Test cases for RequestIdMiddleware"""

    def setup_method(self):
        """Set up test fixtures before each test"""
        self.middleware = RequestIdMiddleware(app=MagicMock())

    @pytest.mark.asyncio
    async def test_dispatch_with_valid_request_id_header(self):
        """Test dispatch with valid UUID in x-exosphere-request-id header"""
        # Setup
        valid_uuid = str(uuid.uuid4())
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-exosphere-request-id": valid_uuid}
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.state = MagicMock()

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        mock_call_next = AsyncMock(return_value=mock_response)

        # Mock time.time for consistent timing
        with patch('time.time', side_effect=[1000.0, 1000.5]):  # 500ms duration
            with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        # Assertions
        assert mock_request.state.x_exosphere_request_id == valid_uuid
        assert mock_response.headers["x-exosphere-request-id"] == valid_uuid
        assert result == mock_response

        # Check logging calls
        assert mock_logger.info.call_count == 2
        
        # First log call - request received
        first_call_args = mock_logger.info.call_args_list[0]
        assert first_call_args[0][0] == "request received"
        assert first_call_args[1]["x_exosphere_request_id"] == valid_uuid
        assert first_call_args[1]["method"] == "GET"
        assert first_call_args[1]["url"] == "/test"
        
        # Second log call - request processed
        second_call_args = mock_logger.info.call_args_list[1]
        assert second_call_args[0][0] == "request processed"
        assert second_call_args[1]["x_exosphere_request_id"] == valid_uuid
        assert second_call_args[1]["response_time"] == 500.0  # 500ms
        assert second_call_args[1]["status_code"] == 200

    @pytest.mark.asyncio
    async def test_dispatch_without_request_id_header_generates_new_uuid(self):
        """Test dispatch generates new UUID when no x-exosphere-request-id header"""
        # Setup
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.state = MagicMock()

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201
        mock_response.headers = {}

        mock_call_next = AsyncMock(return_value=mock_response)

        with patch('time.time', side_effect=[2000.0, 2000.1]):  # 100ms duration
            with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        # Assertions
        generated_uuid = mock_request.state.x_exosphere_request_id
        assert generated_uuid is not None
        
        # Verify it's a valid UUID
        uuid.UUID(generated_uuid)  # Should not raise exception
        
        assert mock_response.headers["x-exosphere-request-id"] == generated_uuid
        assert result == mock_response

        # Check logging
        assert mock_logger.info.call_count == 2
        first_call_args = mock_logger.info.call_args_list[0]
        assert first_call_args[1]["x_exosphere_request_id"] == generated_uuid
        assert first_call_args[1]["method"] == "POST"
        assert first_call_args[1]["url"] == "/api/test"

    @pytest.mark.asyncio
    async def test_dispatch_with_invalid_uuid_generates_new_uuid(self):
        """Test dispatch generates new UUID when x-exosphere-request-id is invalid"""
        # Setup
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-exosphere-request-id": "invalid-uuid"}
        mock_request.method = "PUT"
        mock_request.url.path = "/api/update"
        mock_request.state = MagicMock()

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        mock_call_next = AsyncMock(return_value=mock_response)

        with patch('time.time', side_effect=[3000.0, 3001.0]):  # 1000ms duration
            with patch('app.middlewares.request_id_middleware.logger'):
                await self.middleware.dispatch(mock_request, mock_call_next)

        # Assertions
        generated_uuid = mock_request.state.x_exosphere_request_id
        assert generated_uuid != "invalid-uuid"
        
        # Verify it's a valid UUID
        uuid.UUID(generated_uuid)  # Should not raise exception
        
        assert mock_response.headers["x-exosphere-request-id"] == generated_uuid

    @pytest.mark.asyncio
    async def test_dispatch_with_malformed_uuid_generates_new_uuid(self):
        """Test dispatch generates new UUID when x-exosphere-request-id is malformed"""
        test_cases = [
            "12345",  # Too short
            "not-a-uuid-at-all",  # Not UUID format
            "123e4567-e89b-12d3-a456-42661419",  # Missing last part
            "123e4567-e89b-12d3-a456-426614174000-extra",  # Too long
            "",  # Empty string
            "   ",  # Whitespace only
        ]

        for invalid_uuid in test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.headers = {"x-exosphere-request-id": invalid_uuid}
            mock_request.method = "GET"
            mock_request.url.path = "/test"
            mock_request.state = MagicMock()

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200
            mock_response.headers = {}

            mock_call_next = AsyncMock(return_value=mock_response)

            with patch('time.time', side_effect=[1000.0, 1000.1]):
                with patch('app.middlewares.request_id_middleware.logger'):
                    await self.middleware.dispatch(mock_request, mock_call_next)

            # Should have generated a new valid UUID
            generated_uuid = mock_request.state.x_exosphere_request_id
            assert generated_uuid != invalid_uuid
            uuid.UUID(generated_uuid)  # Should not raise exception

    @pytest.mark.asyncio
    async def test_dispatch_response_time_calculation(self):
        """Test that response time is calculated correctly in milliseconds"""
        # Setup
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.state = MagicMock()

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        mock_call_next = AsyncMock(return_value=mock_response)

        # Test different time durations
        test_cases = [
            (1000.0, 1000.0, 0.0),      # 0ms
            (1000.0, 1000.1, 100.0),    # 100ms
            (1000.0, 1001.0, 1000.0),   # 1000ms (1 second)
            (1000.0, 1002.5, 2500.0),   # 2500ms (2.5 seconds)
        ]

        for start_time, end_time, expected_ms in test_cases:
            with patch('time.time', side_effect=[start_time, end_time]):
                with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                    await self.middleware.dispatch(mock_request, mock_call_next)

            # Check the response time in the second log call
            second_call_args = mock_logger.info.call_args_list[1]
            assert abs(second_call_args[1]["response_time"] - expected_ms) < 0.1

    @pytest.mark.asyncio
    async def test_dispatch_preserves_response_properties(self):
        """Test that dispatch preserves all response properties"""
        # Setup
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.state = MagicMock()

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json", "Custom-Header": "custom-value"}

        mock_call_next = AsyncMock(return_value=mock_response)

        with patch('time.time', side_effect=[1000.0, 1000.1]):
            with patch('app.middlewares.request_id_middleware.logger'):
                result = await self.middleware.dispatch(mock_request, mock_call_next)

        # Should preserve all response properties and add request ID header
        assert result == mock_response
        assert result.status_code == 404
        assert result.headers["Content-Type"] == "application/json"
        assert result.headers["Custom-Header"] == "custom-value"
        assert "x-exosphere-request-id" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_logs_different_request_methods_and_paths(self):
        """Test that dispatch logs different HTTP methods and paths correctly"""
        test_cases = [
            ("GET", "/api/users"),
            ("POST", "/api/users"),
            ("PUT", "/api/users/123"),
            ("DELETE", "/api/users/123"),
            ("PATCH", "/api/users/123"),
            ("HEAD", "/health"),
            ("OPTIONS", "/api/cors"),
        ]

        for method, path in test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.headers = {}
            mock_request.method = method
            mock_request.url.path = path
            mock_request.state = MagicMock()

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200
            mock_response.headers = {}

            mock_call_next = AsyncMock(return_value=mock_response)

            with patch('time.time', side_effect=[1000.0, 1000.1]):
                with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                    await self.middleware.dispatch(mock_request, mock_call_next)

            # Check first log call contains correct method and URL
            first_call_args = mock_logger.info.call_args_list[0]
            assert first_call_args[1]["method"] == method
            assert first_call_args[1]["url"] == path

    @pytest.mark.asyncio
    async def test_dispatch_logs_different_response_status_codes(self):
        """Test that dispatch logs different response status codes correctly"""
        status_codes = [200, 201, 400, 401, 404, 500, 502, 503]

        for status_code in status_codes:
            mock_request = MagicMock(spec=Request)
            mock_request.headers = {}
            mock_request.method = "GET"
            mock_request.url.path = "/test"
            mock_request.state = MagicMock()

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = status_code
            mock_response.headers = {}

            mock_call_next = AsyncMock(return_value=mock_response)

            with patch('time.time', side_effect=[1000.0, 1000.1]):
                with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                    await self.middleware.dispatch(mock_request, mock_call_next)

            # Check second log call contains correct status code
            second_call_args = mock_logger.info.call_args_list[1]
            assert second_call_args[1]["status_code"] == status_code

    @pytest.mark.asyncio
    async def test_dispatch_uuid_consistency_throughout_request(self):
        """Test that the same UUID is used throughout the request lifecycle"""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.state = MagicMock()

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        mock_call_next = AsyncMock(return_value=mock_response)

        with patch('time.time', side_effect=[1000.0, 1000.1]):
            with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                await self.middleware.dispatch(mock_request, mock_call_next)

        # Get the UUID from request state
        request_uuid = mock_request.state.x_exosphere_request_id
        
        # Get the UUID from response header
        response_uuid = mock_response.headers["x-exosphere-request-id"]
        
        # Get UUIDs from both log calls
        first_log_uuid = mock_logger.info.call_args_list[0][1]["x_exosphere_request_id"]
        second_log_uuid = mock_logger.info.call_args_list[1][1]["x_exosphere_request_id"]

        # All should be the same
        assert request_uuid == response_uuid == first_log_uuid == second_log_uuid

    @pytest.mark.asyncio
    async def test_dispatch_handles_case_sensitive_header(self):
        """Test that header matching is case-insensitive as per HTTP standards"""
        # Setup with different case variations
        header_variations = [
            "x-exosphere-request-id",
            "X-Exosphere-Request-Id", 
            "X-EXOSPHERE-REQUEST-ID",
            "x-Exosphere-Request-Id"
        ]

        valid_uuid = str(uuid.uuid4())

        for header_name in header_variations:
            mock_request = MagicMock(spec=Request)
            # Mock headers.get to be case-insensitive like real Starlette
            def case_insensitive_get(key):
                if key.lower() == "x-exosphere-request-id":
                    return valid_uuid
                return None
            
            mock_request.headers.get = case_insensitive_get
            mock_request.method = "GET"
            mock_request.url.path = "/test"
            mock_request.state = MagicMock()

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200
            mock_response.headers = {}

            mock_call_next = AsyncMock(return_value=mock_response)

            with patch('time.time', side_effect=[1000.0, 1000.1]):
                with patch('app.middlewares.request_id_middleware.logger'):
                    await self.middleware.dispatch(mock_request, mock_call_next)

            # Should use the provided UUID regardless of header case
            assert mock_request.state.x_exosphere_request_id == valid_uuid

    @pytest.mark.asyncio 
    async def test_dispatch_exception_handling(self):
        """Test middleware behavior when call_next raises an exception"""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.state = MagicMock()

        # Mock call_next to raise an exception
        mock_call_next = AsyncMock(side_effect=Exception("Test exception"))

        with patch('time.time', side_effect=[1000.0, 1000.1]):
            with patch('app.middlewares.request_id_middleware.logger') as mock_logger:
                with pytest.raises(Exception, match="Test exception"):
                    await self.middleware.dispatch(mock_request, mock_call_next)

        # Should still log the request received, but not the processed log
        assert mock_logger.info.call_count == 1
        first_call_args = mock_logger.info.call_args_list[0]
        assert first_call_args[0][0] == "request received"
        
        # Request state should still be set
        assert hasattr(mock_request.state, 'x_exosphere_request_id')
        uuid.UUID(mock_request.state.x_exosphere_request_id)  # Should be valid UUID