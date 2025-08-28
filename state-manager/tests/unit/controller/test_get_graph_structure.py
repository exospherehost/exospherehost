import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId

from app.controller.get_graph_structure import get_graph_structure
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.models.graph_structure_models import GraphStructureResponse, GraphNode, GraphEdge


class TestGetGraphStructure:
    """Test cases for get_graph_structure function"""

    @pytest.mark.asyncio
    async def test_get_graph_structure_success(self):
        """Test successful graph structure building"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        # Create mock states
        mock_state1 = MagicMock()
        mock_state1.id = ObjectId()
        mock_state1.node_name = "node1"
        mock_state1.identifier = "id1"
        mock_state1.status = StateStatusEnum.SUCCESS
        mock_state1.inputs = {"input1": "value1"}
        mock_state1.outputs = {"output1": "result1"}
        mock_state1.error = None
        mock_state1.created_at = datetime.now()
        mock_state1.updated_at = datetime.now()
        mock_state1.graph_name = "test_graph"
        mock_state1.parents = {}

        mock_state2 = MagicMock()
        mock_state2.id = ObjectId()
        mock_state2.node_name = "node2"
        mock_state2.identifier = "id2"
        mock_state2.status = StateStatusEnum.CREATED
        mock_state2.inputs = {"input2": "value2"}
        mock_state2.outputs = {"output2": "result2"}
        mock_state2.error = None
        mock_state2.created_at = datetime.now()
        mock_state2.updated_at = datetime.now()
        mock_state2.graph_name = "test_graph"
        # Use the actual state1 ID as parent
        mock_state2.parents = {"id1": mock_state1.id}

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = [mock_state1, mock_state2]
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify the result
            assert isinstance(result, GraphStructureResponse)
            assert result.namespace == namespace
            assert result.run_id == run_id
            assert result.graph_name == "test_graph"
            assert result.node_count == 2
            assert result.edge_count == 1
            assert len(result.nodes) == 2
            assert len(result.edges) == 1
            assert len(result.root_states) == 1

            # Verify nodes
            node1 = result.nodes[0]
            assert node1.id == str(mock_state1.id)
            assert node1.node_name == "node1"
            assert node1.identifier == "id1"
            assert node1.status == StateStatusEnum.SUCCESS

            # Verify edges
            edge = result.edges[0]
            assert edge.source == str(mock_state1.id)
            assert edge.target == str(mock_state2.id)
            assert edge.source_output == "id1"
            assert edge.target_input == "id1"

            # Verify execution summary
            assert result.execution_summary["SUCCESS"] == 1
            assert result.execution_summary["CREATED"] == 1

    @pytest.mark.asyncio
    async def test_get_graph_structure_no_states(self):
        """Test graph structure building when no states are found"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = []
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify empty result
            assert isinstance(result, GraphStructureResponse)
            assert result.namespace == namespace
            assert result.run_id == run_id
            assert result.graph_name == ""
            assert result.node_count == 0
            assert result.edge_count == 0
            assert len(result.nodes) == 0
            assert len(result.edges) == 0
            assert len(result.root_states) == 0
            assert result.execution_summary == {}

    @pytest.mark.asyncio
    async def test_get_graph_structure_with_errors(self):
        """Test graph structure building with states that have errors"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        # Create mock state with error
        mock_state = MagicMock()
        mock_state.id = ObjectId()
        mock_state.node_name = "error_node"
        mock_state.identifier = "error_id"
        mock_state.status = StateStatusEnum.ERRORED
        mock_state.inputs = {}
        mock_state.outputs = {}
        mock_state.error = "Something went wrong"
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()
        mock_state.graph_name = "test_graph"
        mock_state.parents = {}

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = [mock_state]
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify the result
            assert result.node_count == 1
            assert result.edge_count == 0
            assert len(result.root_states) == 1

            node = result.nodes[0]
            assert node.status == StateStatusEnum.ERRORED
            assert node.error == "Something went wrong"
            assert result.execution_summary["ERRORED"] == 1

    @pytest.mark.asyncio
    async def test_get_graph_structure_complex_parents(self):
        """Test graph structure building with complex parent relationships"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        # Create mock states with multiple parents
        mock_state1 = MagicMock()
        mock_state1.id = ObjectId()
        mock_state1.node_name = "parent1"
        mock_state1.identifier = "parent1"
        mock_state1.status = StateStatusEnum.SUCCESS
        mock_state1.inputs = {}
        mock_state1.outputs = {}
        mock_state1.error = None
        mock_state1.created_at = datetime.now()
        mock_state1.updated_at = datetime.now()
        mock_state1.graph_name = "test_graph"
        mock_state1.parents = {}

        mock_state2 = MagicMock()
        mock_state2.id = ObjectId()
        mock_state2.node_name = "parent2"
        mock_state2.identifier = "parent2"
        mock_state2.status = StateStatusEnum.SUCCESS
        mock_state2.inputs = {}
        mock_state2.outputs = {}
        mock_state2.error = None
        mock_state2.created_at = datetime.now()
        mock_state2.updated_at = datetime.now()
        mock_state2.graph_name = "test_graph"
        mock_state2.parents = {}

        # Child state with multiple parents (accumulated)
        mock_child = MagicMock()
        mock_child.id = ObjectId()
        mock_child.node_name = "child"
        mock_child.identifier = "child"
        mock_child.status = StateStatusEnum.CREATED
        mock_child.inputs = {}
        mock_child.outputs = {}
        mock_child.error = None
        mock_child.created_at = datetime.now()
        mock_child.updated_at = datetime.now()
        mock_child.graph_name = "test_graph"
        # Parents dict with insertion order preserved - use actual state IDs
        mock_child.parents = {"parent1": mock_state1.id, "parent2": mock_state2.id}

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = [mock_state1, mock_state2, mock_child]
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify the result
            assert result.node_count == 3
            assert result.edge_count == 1  # Only direct parent relationship
            assert len(result.root_states) == 2

            # Should only create edge for the most recent parent (parent2)
            edge = result.edges[0]
            assert edge.source == str(mock_state2.id)
            assert edge.target == str(mock_child.id)
            assert edge.source_output == "parent2"
            assert edge.target_input == "parent2"

    @pytest.mark.asyncio
    async def test_get_graph_structure_parent_not_in_nodes(self):
        """Test graph structure building when parent is not in the same run"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        # Create mock state with parent that doesn't exist in the same run
        mock_state = MagicMock()
        mock_state.id = ObjectId()
        mock_state.node_name = "child"
        mock_state.identifier = "child"
        mock_state.status = StateStatusEnum.CREATED
        mock_state.inputs = {}
        mock_state.outputs = {}
        mock_state.error = None
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()
        mock_state.graph_name = "test_graph"
        mock_state.parents = {"missing_parent": ObjectId()}

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = [mock_state]
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify the result - no edges should be created
            assert result.node_count == 1
            assert result.edge_count == 0
            assert len(result.root_states) == 0  # Not a root state since it has parents

    @pytest.mark.asyncio
    async def test_get_graph_structure_exception_handling(self):
        """Test graph structure building with exception handling"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.side_effect = Exception("Database error")
            mock_state_class.find.return_value = mock_find

            with pytest.raises(Exception, match="Database error"):
                await get_graph_structure(namespace, run_id, request_id)

    @pytest.mark.asyncio
    async def test_get_graph_structure_multiple_statuses(self):
        """Test graph structure building with multiple status types"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        # Create mock states with different statuses
        states = []
        statuses = [StateStatusEnum.CREATED, StateStatusEnum.QUEUED, StateStatusEnum.EXECUTED, 
                   StateStatusEnum.SUCCESS, StateStatusEnum.ERRORED, StateStatusEnum.NEXT_CREATED_ERROR]

        for i, status in enumerate(statuses):
            mock_state = MagicMock()
            mock_state.id = ObjectId()
            mock_state.node_name = f"node{i}"
            mock_state.identifier = f"id{i}"
            mock_state.status = status
            mock_state.inputs = {}
            mock_state.outputs = {}
            mock_state.error = None
            mock_state.created_at = datetime.now()
            mock_state.updated_at = datetime.now()
            mock_state.graph_name = "test_graph"
            mock_state.parents = {}
            states.append(mock_state)

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = states
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify execution summary has all statuses
            assert result.node_count == 6
            assert result.edge_count == 0
            assert len(result.root_states) == 6

            for status in statuses:
                assert result.execution_summary[status.value] == 1

    @pytest.mark.asyncio
    async def test_get_graph_structure_with_position_data(self):
        """Test graph structure building with position data in nodes"""
        namespace = "test_namespace"
        run_id = "test_run_id"
        request_id = "test_request_id"

        # Create mock state
        mock_state = MagicMock()
        mock_state.id = ObjectId()
        mock_state.node_name = "test_node"
        mock_state.identifier = "test_id"
        mock_state.status = StateStatusEnum.SUCCESS
        mock_state.inputs = {}
        mock_state.outputs = {}
        mock_state.error = None
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()
        mock_state.graph_name = "test_graph"
        mock_state.parents = {}

        with patch('app.controller.get_graph_structure.State') as mock_state_class:
            mock_find = AsyncMock()
            mock_find.to_list.return_value = [mock_state]
            mock_state_class.find.return_value = mock_find

            result = await get_graph_structure(namespace, run_id, request_id)

            # Verify node has position set to None (as per implementation)
            node = result.nodes[0]
            assert node.position is None 