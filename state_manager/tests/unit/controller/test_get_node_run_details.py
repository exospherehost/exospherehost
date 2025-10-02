import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

from app.controller.get_node_run_details import get_node_run_details
from app.models.state_status_enum import StateStatusEnum
from app.models.node_run_details_models import NodeRunDetailsResponse


class TestGetNodeRunDetails:
    """Test cases for get_node_run_details function"""

    @pytest.mark.asyncio
    async def test_get_node_run_details_success(self):
        """Test successful node run details retrieval"""
        namespace = "test_namespace"
        graph_name = "test_graph"
        run_id = "test_run_id"
        node_id = str(ObjectId())
        request_id = "test_request_id"

        # Create mock state
        mock_state = MagicMock()
        mock_state.id = ObjectId(node_id)
        mock_state.node_name = "test_node"
        mock_state.identifier = "test_identifier"
        mock_state.graph_name = graph_name
        mock_state.run_id = run_id
        mock_state.status = StateStatusEnum.SUCCESS
        mock_state.inputs = {"input1": "value1"}
        mock_state.outputs = {"output1": "result1"}
        mock_state.error = None
        mock_state.parents = {"parent1": ObjectId()}
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()

        with patch('app.controller.get_node_run_details.State') as mock_state_class:
            mock_state_class.find_one = AsyncMock(return_value=mock_state)

            result = await get_node_run_details(namespace, graph_name, run_id, node_id, request_id)

            # Verify the result
            assert isinstance(result, NodeRunDetailsResponse)
            assert result.id == node_id
            assert result.node_name == "test_node"
            assert result.identifier == "test_identifier"
            assert result.graph_name == graph_name
            assert result.run_id == run_id
            assert result.status == StateStatusEnum.SUCCESS
            assert result.inputs == {"input1": "value1"}
            assert result.outputs == {"output1": "result1"}
            assert result.error is None
            assert len(result.parents) == 1

    @pytest.mark.asyncio
    async def test_get_node_run_details_not_found(self):
        """Test node run details when node is not found"""
        namespace = "test_namespace"
        graph_name = "test_graph"
        run_id = "test_run_id"
        node_id = str(ObjectId())
        request_id = "test_request_id"

        with patch('app.controller.get_node_run_details.State') as mock_state_class:
            mock_state_class.find_one = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_node_run_details(namespace, graph_name, run_id, node_id, request_id)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_node_run_details_invalid_node_id(self):
        """Test node run details with invalid node ID format"""
        namespace = "test_namespace"
        graph_name = "test_graph"
        run_id = "test_run_id"
        node_id = "invalid_id"
        request_id = "test_request_id"

        with pytest.raises(HTTPException) as exc_info:
            await get_node_run_details(namespace, graph_name, run_id, node_id, request_id)

        assert exc_info.value.status_code == 400
        assert "Invalid node ID format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_node_run_details_with_error(self):
        """Test node run details retrieval for a node with error"""
        namespace = "test_namespace"
        graph_name = "test_graph"
        run_id = "test_run_id"
        node_id = str(ObjectId())
        request_id = "test_request_id"

        # Create mock state with error
        mock_state = MagicMock()
        mock_state.id = ObjectId(node_id)
        mock_state.node_name = "error_node"
        mock_state.identifier = "error_identifier"
        mock_state.graph_name = graph_name
        mock_state.run_id = run_id
        mock_state.status = StateStatusEnum.ERRORED
        mock_state.inputs = {"input1": "value1"}
        mock_state.outputs = {}
        mock_state.error = "Something went wrong"
        mock_state.parents = {}
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()

        with patch('app.controller.get_node_run_details.State') as mock_state_class:
            mock_state_class.find_one = AsyncMock(return_value=mock_state)

            result = await get_node_run_details(namespace, graph_name, run_id, node_id, request_id)

            # Verify the result
            assert result.status == StateStatusEnum.ERRORED
            assert result.error == "Something went wrong"
            assert result.outputs == {}

    @pytest.mark.asyncio
    async def test_get_node_run_details_database_exception(self):
        """Test node run details with database exception"""
        namespace = "test_namespace"
        graph_name = "test_graph"
        run_id = "test_run_id"
        node_id = str(ObjectId())
        request_id = "test_request_id"

        with patch('app.controller.get_node_run_details.State') as mock_state_class:
            mock_state_class.find_one = AsyncMock(side_effect=Exception("Database error"))

            with pytest.raises(HTTPException) as exc_info:
                await get_node_run_details(namespace, graph_name, run_id, node_id, request_id)

            assert exc_info.value.status_code == 500
            assert "Internal server error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_node_run_details_empty_timestamps(self):
        """Test node run details with empty timestamps"""
        namespace = "test_namespace"
        graph_name = "test_graph"
        run_id = "test_run_id"
        node_id = str(ObjectId())
        request_id = "test_request_id"

        # Create mock state with None timestamps
        mock_state = MagicMock()
        mock_state.id = ObjectId(node_id)
        mock_state.node_name = "test_node"
        mock_state.identifier = "test_identifier"
        mock_state.graph_name = graph_name
        mock_state.run_id = run_id
        mock_state.status = StateStatusEnum.CREATED
        mock_state.inputs = {}
        mock_state.outputs = {}
        mock_state.error = None
        mock_state.parents = {}
        mock_state.created_at = None
        mock_state.updated_at = None

        with patch('app.controller.get_node_run_details.State') as mock_state_class:
            mock_state_class.find_one = AsyncMock(return_value=mock_state)

            result = await get_node_run_details(namespace, graph_name, run_id, node_id, request_id)

            # Verify the result handles None timestamps
            assert result.created_at == ""
            assert result.updated_at == "" 