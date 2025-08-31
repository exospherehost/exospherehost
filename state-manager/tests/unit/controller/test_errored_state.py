import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.controller.errored_state import errored_state
from app.models.errored_models import ErroredRequestModel
from app.models.state_status_enum import StateStatusEnum


class TestErroredState:
    """Test cases for errored_state function"""

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_state_id(self):
        return PydanticObjectId()

    @pytest.fixture
    def mock_errored_request(self):
        return ErroredRequestModel(
            error="Test error message"
        )

    @pytest.fixture
    def mock_state_queued(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.QUEUED
        state.graph_name = "test_graph"
        state.retry_count = 0
        state.node_name = "test_node"
        state.namespace_name = "test_namespace"
        state.identifier = "test_identifier"
        state.run_id = "test_run_id"
        state.inputs = {}
        state.parents = []
        state.does_unites = False
        state.fanout_id = None
        return state

    @pytest.fixture
    def mock_state_executed(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.EXECUTED
        state.graph_name = "test_graph"
        state.retry_count = 0
        state.node_name = "test_node"
        state.namespace_name = "test_namespace"
        state.identifier = "test_identifier"
        state.run_id = "test_run_id"
        state.inputs = {}
        state.parents = []
        state.does_unites = False
        state.fanout_id = None
        return state

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_success_queued(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_queued,
        mock_request_id
    ):
        """Test successful error marking of queued state"""      
        
        # Mock GraphTemplate.get to return a valid graph template
        mock_graph_template = MagicMock()
        mock_graph_template.retry_policy.max_retries = 3
        mock_graph_template.retry_policy.compute_delay = MagicMock(return_value=1000)
        mock_graph_template_class.get = AsyncMock(return_value=mock_graph_template)
        
        # Mock State constructor and insert method
        mock_retry_state = MagicMock()
        mock_retry_state.insert = AsyncMock(return_value=mock_retry_state)
        mock_state_class.return_value = mock_retry_state
        
        mock_state_queued.save = AsyncMock()     
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            mock_errored_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert mock_state_class.find_one.call_count == 1  # Called once for finding
        

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_success_executed(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_executed,
        mock_request_id
    ):
        """Test that executed states cannot be marked as errored"""
        # Arrange
        mock_state_executed.status = StateStatusEnum.EXECUTED
        mock_state_class.find_one = AsyncMock(return_value=mock_state_executed)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is already executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is not found"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_invalid_status_created(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is in CREATED status (invalid for error marking)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.CREATED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not queued or executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_invalid_status_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is already in ERRORED status"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.ERRORED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not queued or executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_already_executed(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is already executed (should not allow error marking)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.EXECUTED
        mock_state.graph_name = "test_graph"
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is already executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.find_one = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_with_different_error_message(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_queued,
        mock_request_id
    ):
        """Test error marking with different error message"""
        # Arrange
        different_error_request = ErroredRequestModel(
            error="Different error message"
        )
        
        # Mock GraphTemplate.get to return a valid graph template
        mock_graph_template = MagicMock()
        mock_graph_template.retry_policy.max_retries = 3
        mock_graph_template.retry_policy.compute_delay = MagicMock(return_value=1000)
        mock_graph_template_class.get = AsyncMock(return_value=mock_graph_template)
        
        # Mock State constructor and insert method
        mock_retry_state = MagicMock()
        mock_retry_state.insert = AsyncMock(return_value=mock_retry_state)
        mock_state_class.return_value = mock_retry_state
        
        mock_state_queued.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            different_error_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert mock_state_class.find_one.call_count == 1  # Called once for finding
        assert mock_state_queued.error == "Different error message"

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_graph_template_not_found(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_queued,
        mock_request_id
    ):
        """Test when graph template is not found"""
        # Arrange
        mock_state_queued.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)
        
        # Mock GraphTemplate.get to raise ValueError with "Graph template not found"
        mock_graph_template_class.get = AsyncMock(side_effect=ValueError("Graph template not found"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Graph template not found"

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_graph_template_other_error(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_queued,
        mock_request_id
    ):
        """Test when graph template raises other exceptions"""
        # Arrange
        mock_state_queued.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)
        
        # Mock GraphTemplate.get to raise a different exception
        mock_graph_template_class.get = AsyncMock(side_effect=Exception("Database connection error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database connection error"

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_duplicate_key_error(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_queued,
        mock_request_id
    ):
        """Test when creating retry state encounters DuplicateKeyError"""
        # Arrange
        mock_state_queued.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)
        
        # Mock GraphTemplate.get to return a valid graph template
        mock_graph_template = MagicMock()
        mock_graph_template.retry_policy.max_retries = 3
        mock_graph_template.retry_policy.compute_delay = MagicMock(return_value=1000)
        mock_graph_template_class.get = AsyncMock(return_value=mock_graph_template)
        
        # Mock State constructor and insert method to raise DuplicateKeyError
        mock_retry_state = MagicMock()
        mock_retry_state.insert = AsyncMock(side_effect=DuplicateKeyError("Duplicate key error"))
        mock_state_class.return_value = mock_retry_state

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            mock_errored_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert result.retry_created == False
        assert mock_state_queued.status == StateStatusEnum.ERRORED
        assert mock_state_queued.error == mock_errored_request.error

    @patch('app.controller.errored_state.State')
    @patch('app.controller.errored_state.GraphTemplate')
    async def test_errored_state_max_retries_reached(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state has reached max retries"""
        # Arrange
        mock_state = MagicMock()
        mock_state.id = PydanticObjectId()
        mock_state.status = StateStatusEnum.QUEUED
        mock_state.graph_name = "test_graph"
        mock_state.retry_count = 3  # Already at max retries
        mock_state.node_name = "test_node"
        mock_state.namespace_name = "test_namespace"
        mock_state.identifier = "test_identifier"
        mock_state.run_id = "test_run_id"
        mock_state.inputs = {}
        mock_state.parents = []
        mock_state.does_unites = False
        mock_state.fanout_id = None
        mock_state.save = AsyncMock()
        
        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        
        # Mock GraphTemplate.get to return a valid graph template with max_retries = 3
        mock_graph_template = MagicMock()
        mock_graph_template.retry_policy.max_retries = 3
        mock_graph_template_class.get = AsyncMock(return_value=mock_graph_template)

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            mock_errored_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert result.retry_created == False
        assert mock_state.status == StateStatusEnum.ERRORED
        assert mock_state.error == mock_errored_request.error
        # Verify that State constructor was not called (no retry created)
        mock_state_class.assert_not_called()

    @patch('app.controller.errored_state.State')
    async def test_errored_state_general_exception(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test handling of general exceptions in the main try-catch block"""
        # Arrange
        mock_state_class.find_one = AsyncMock(side_effect=Exception("Unexpected error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Unexpected error"

