import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.controller.enqueue_states import enqueue_states
from app.models.state_status_enum import StateStatusEnum
from app.models.enqueue_request import EnqueueRequestModel


class TestEnqueueStatesComprehensive:
    """Comprehensive test cases for enqueue_states function"""

    @pytest.mark.asyncio
    async def test_enqueue_states_success(self):
        """Test successful enqueue states"""
        # Create mock state data
        mock_state_data = {
            "id": "state1",
            "node_name": "test_node",
            "identifier": "test_identifier",
            "inputs": {"test": "input"},
            "created_at": datetime.now()
        }

        with patch('app.controller.enqueue_states.State') as mock_state_class:
            # Mock the collection
            mock_collection = MagicMock()
            mock_collection.find_one_and_update = AsyncMock(return_value=mock_state_data)
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            # Mock the State constructor
            mock_state_instance = MagicMock()
            mock_state_instance.id = "state1"
            mock_state_instance.node_name = "test_node"
            mock_state_instance.identifier = "test_identifier"
            mock_state_instance.inputs = {"test": "input"}
            mock_state_instance.created_at = datetime.now()
            mock_state_class.return_value = mock_state_instance

            request_model = EnqueueRequestModel(nodes=["test_node"], batch_size=1)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            assert result.count == 1
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 1
            assert result.states[0].state_id == "state1"
            assert result.states[0].node_name == "test_node"

    @pytest.mark.asyncio
    async def test_enqueue_states_no_states_found(self):
        """Test enqueue states when no states are found"""
        with patch('app.controller.enqueue_states.State') as mock_state_class:
            mock_collection = MagicMock()
            mock_collection.find_one_and_update = AsyncMock(return_value=None)
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            request_model = EnqueueRequestModel(nodes=["test_node"], batch_size=1)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            assert result.count == 0
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 0

    @pytest.mark.asyncio
    async def test_enqueue_states_database_error(self):
        """Test enqueue states with database error"""
        with patch('app.controller.enqueue_states.State') as mock_state_class:
            mock_collection = MagicMock()
            mock_collection.find_one_and_update = AsyncMock(side_effect=Exception("Database connection error"))
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            request_model = EnqueueRequestModel(nodes=["test_node"], batch_size=1)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            # The function handles the exception gracefully and returns empty result
            assert result.count == 0
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 0

    @pytest.mark.asyncio
    async def test_enqueue_states_partial_success(self):
        """Test enqueue states with partial success"""
        # Create mock state data
        mock_state_data = {
            "id": "state1",
            "node_name": "test_node",
            "identifier": "test_identifier",
            "inputs": {"test": "input"},
            "created_at": datetime.now()
        }

        with patch('app.controller.enqueue_states.State') as mock_state_class:
            mock_collection = MagicMock()
            # First call succeeds, second call fails
            mock_collection.find_one_and_update = AsyncMock(side_effect=[
                mock_state_data,  # First call returns state data
                Exception("Update failed for state2")  # Second call fails
            ])
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            # Mock the State constructor
            mock_state_instance = MagicMock()
            mock_state_instance.id = "state1"
            mock_state_instance.node_name = "test_node"
            mock_state_instance.identifier = "test_identifier"
            mock_state_instance.inputs = {"test": "input"}
            mock_state_instance.created_at = datetime.now()
            mock_state_class.return_value = mock_state_instance

            request_model = EnqueueRequestModel(nodes=["test_node"], batch_size=2)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            # Should return response with one successful state
            assert result.count == 1
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 1
            assert result.states[0].state_id == "state1"

    @pytest.mark.asyncio
    async def test_enqueue_states_large_batch_size(self):
        """Test enqueue states with large batch size"""
        # Create mock state data
        mock_state_data = {
            "id": "state1",
            "node_name": "test_node",
            "identifier": "test_identifier",
            "inputs": {"test": "input"},
            "created_at": datetime.now()
        }

        with patch('app.controller.enqueue_states.State') as mock_state_class:
            mock_collection = MagicMock()
            mock_collection.find_one_and_update = AsyncMock(return_value=mock_state_data)
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            # Mock the State constructor
            mock_state_instance = MagicMock()
            mock_state_instance.id = "state1"
            mock_state_instance.node_name = "test_node"
            mock_state_instance.identifier = "test_identifier"
            mock_state_instance.inputs = {"test": "input"}
            mock_state_instance.created_at = datetime.now()
            mock_state_class.return_value = mock_state_instance

            request_model = EnqueueRequestModel(nodes=["test_node"], batch_size=10)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            # Should create 10 tasks and find 10 states (one for each task)
            assert result.count == 10
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 10

    @pytest.mark.asyncio
    async def test_enqueue_states_empty_nodes_list(self):
        """Test enqueue states with empty nodes list"""
        with patch('app.controller.enqueue_states.State') as mock_state_class:
            mock_collection = MagicMock()
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            request_model = EnqueueRequestModel(nodes=[], batch_size=1)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            assert result.count == 0
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 0

    @pytest.mark.asyncio
    async def test_enqueue_states_multiple_nodes(self):
        """Test enqueue states with multiple nodes"""
        # Create mock state data
        mock_state_data1 = {
            "id": "state1",
            "node_name": "node1",
            "identifier": "identifier1",
            "inputs": {"test": "input1"},
            "created_at": datetime.now()
        }
        mock_state_data2 = {
            "id": "state2",
            "node_name": "node2",
            "identifier": "identifier2",
            "inputs": {"test": "input2"},
            "created_at": datetime.now()
        }

        with patch('app.controller.enqueue_states.State') as mock_state_class:
            mock_collection = MagicMock()
            mock_collection.find_one_and_update = AsyncMock(side_effect=[mock_state_data1, mock_state_data2])
            mock_state_class.get_pymongo_collection.return_value = mock_collection

            # Mock the State constructor
            mock_state_instance1 = MagicMock()
            mock_state_instance1.id = "state1"
            mock_state_instance1.node_name = "node1"
            mock_state_instance1.identifier = "identifier1"
            mock_state_instance1.inputs = {"test": "input1"}
            mock_state_instance1.created_at = datetime.now()

            mock_state_instance2 = MagicMock()
            mock_state_instance2.id = "state2"
            mock_state_instance2.node_name = "node2"
            mock_state_instance2.identifier = "identifier2"
            mock_state_instance2.inputs = {"test": "input2"}
            mock_state_instance2.created_at = datetime.now()

            mock_state_class.side_effect = [mock_state_instance1, mock_state_instance2]

            request_model = EnqueueRequestModel(nodes=["node1", "node2"], batch_size=2)
            result = await enqueue_states("test_namespace", request_model, "test_request_id")

            assert result.count == 2
            assert result.namespace == "test_namespace"
            assert result.status == StateStatusEnum.QUEUED
            assert len(result.states) == 2
            assert result.states[0].state_id == "state1"
            assert result.states[1].state_id == "state2" 