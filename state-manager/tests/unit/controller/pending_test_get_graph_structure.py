"""
Unit tests for get_graph_structure controller
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from beanie import PydanticObjectId
from datetime import datetime

from app.controller.get_graph_structure import get_graph_structure
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum


def mock_state(id, status, run_id, node_name, namespace_name, identifier, graph_name, inputs, outputs, parents):
    state = MagicMock()
    state.id = id
    state.status = status
    state.run_id= run_id
    state.node_name = node_name
    state.namespace_name = namespace_name
    state.identifier = identifier
    state.graph_name = graph_name
    state.inputs = inputs
    state.outputs = outputs
    state.parents = parents
    return state


@pytest.fixture
def mock_states():
    """Create mock states for testing"""
    state1_id = PydanticObjectId()
    state2_id = PydanticObjectId()
    state3_id = PydanticObjectId()

    state1= mock_state(
        id=state1_id,
        status= StateStatusEnum.SUCCESS,
        node_name="start_node",
        run_id= "test-run-id",
        namespace_name="test_namespace",
        identifier="start_1",
        graph_name="test_graph",
        inputs={"input1": "value1"},
        outputs={"output1"},
        parents={},
    )

    state2= mock_state(
        id=state2_id,
        status= StateStatusEnum.SUCCESS,
        node_name="process_node",
        run_id= "test-run-id",
        namespace_name="test_namespace",
        identifier="process_1",
        graph_name="test_graph",
        inputs={"input2": "value2"},
        outputs={"output2": "result2"},
        parents={"start_1": state1_id}
    )    

    state3= mock_state(
            id=state3_id,
            status= StateStatusEnum.SUCCESS,
            node_name="process_node",
            run_id= "test-run-id",
            namespace_name="test_namespace",
            identifier="process_1",
            graph_name="test_graph",
            inputs={"input2": "value2"},
            outputs={"output2": "result2"},
            parents={"start_1": state1_id}
        )    
    
    return [state1,state2,state3]


@pytest.mark.asyncio
async def test_get_graph_structure_success(mock_states):
    """Test successful graph structure retrieval"""
    namespace = "test_namespace"
    run_id = "test_run_123"
    request_id = "test_request_123"
    
    with patch.object(State, 'find') as mock_find:
        mock_find.return_value.to_list = AsyncMock(return_value=mock_states)
        
        result = await get_graph_structure(namespace, run_id, request_id)
        
        # Verify State.find was called correctly
        mock_find.assert_called_once()
        call_args = mock_find.call_args[0]
        assert len(call_args) == 2
        assert call_args[0] == State.run_id == run_id
        assert call_args[1] == State.namespace_name == namespace
        
        # Verify result structure
        assert result.namespace == namespace
        assert result.run_id == run_id
        assert result.graph_name == "test_graph"
        assert result.node_count == 3
        assert result.edge_count == 2
        assert len(result.nodes) == 3
        assert len(result.edges) == 2
        
        # Verify nodes
        node_ids = [node.id for node in result.nodes]
        assert len(node_ids) == 3
        
        # Verify edges
        edge_sources = [edge.source for edge in result.edges]
        edge_targets = [edge.target for edge in result.edges]
        assert len(edge_sources) == 2
        assert len(edge_targets) == 2
        
        # Verify execution summary
        assert result.execution_summary["SUCCESS"] == 3
        assert any(n.node_name == "start_node" for n in result.root_states)


@pytest.mark.asyncio
async def test_get_graph_structure_no_states():
    """Test graph structure retrieval when no states exist"""
    namespace = "test_namespace"
    run_id = "test_run_123"
    request_id = "test_request_123"
    
    with patch.object(State, 'find') as mock_find:
        mock_find.return_value.to_list = AsyncMock(return_value=[])
        
        result = await get_graph_structure(namespace, run_id, request_id)
        
        # Verify result structure for empty states
        assert result.namespace == namespace
        assert result.run_id == run_id
        assert result.graph_name == ""
        assert result.node_count == 0
        assert result.edge_count == 0
        assert len(result.nodes) == 0
        assert len(result.edges) == 0
        # All states should be initialized to 0
        expected_summary = {status.value: 0 for status in StateStatusEnum}
        assert result.execution_summary == expected_summary
        assert result.root_states == [] 


@pytest.mark.asyncio
async def test_get_graph_structure_with_errors(mock_states):
    """Test graph structure with errored states"""
    namespace = "test_namespace"
    run_id = "test_run_123"
    request_id = "test_request_123"
    
    # Modify one state to have an error
    mock_states[1].status = StateStatusEnum.ERRORED
    mock_states[1].error = "Test error message"
    
    with patch.object(State, 'find') as mock_find:
        mock_find.return_value.to_list = AsyncMock(return_value=mock_states)
        
        result = await get_graph_structure(namespace, run_id, request_id)
        
        # Verify result structure
        assert result.node_count == 3
        assert result.edge_count == 2
        
        # Verify execution summary includes both SUCCESS and ERRORED
        assert result.execution_summary["SUCCESS"] == 2
        assert result.execution_summary["ERRORED"] == 1
        
        # Verify error state is included
        error_nodes = [node for node in result.nodes if node.status == "ERRORED"]
        assert len(error_nodes) == 1
        assert error_nodes[0].error == "Test error message"


@pytest.mark.asyncio
async def test_get_graph_structure_complex_relationships():
    """Test graph structure with complex parent-child relationships"""
    namespace = "test_namespace"
    run_id = "test_run_123"
    request_id = "test_request_123"
    
    # Create states with complex relationships
    state1_id = PydanticObjectId()
    state2_id = PydanticObjectId()
    state3_id = PydanticObjectId()
    state4_id = PydanticObjectId()
    
    states = [
        State(
            id=state1_id,
            node_name="root_node",
            namespace_name="test_namespace",
            identifier="root_1",
            graph_name="test_graph",
            run_id="test_run_123",
            status=StateStatusEnum.SUCCESS,
            inputs={},
            outputs={},
            error=None,
            parents={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        State(
            id=state2_id,
            node_name="child1_node",
            namespace_name="test_namespace",
            identifier="child1_1",
            graph_name="test_graph",
            run_id="test_run_123",
            status=StateStatusEnum.SUCCESS,
            inputs={},
            outputs={},
            error=None,
            parents={"root_1": state1_id},
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        State(
            id=state3_id,
            node_name="child2_node",
            namespace_name="test_namespace",
            identifier="child2_1",
            graph_name="test_graph",
            run_id="test_run_123",
            status=StateStatusEnum.SUCCESS,
            inputs={},
            outputs={},
            error=None,
            parents={"root_1": state1_id},
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        State(
            id=state4_id,
            node_name="final_node",
            namespace_name="test_namespace",
            identifier="final_1",
            graph_name="test_graph",
            run_id="test_run_123",
            status=StateStatusEnum.SUCCESS,
            inputs={},
            outputs={},
            error=None,
            parents={"child1_1": state2_id, "child2_1": state3_id},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    with patch.object(State, 'find') as mock_find:
        mock_find.return_value.to_list = AsyncMock(return_value=states)
        
        result = await get_graph_structure(namespace, run_id, request_id)
        
        # Verify result structure
        assert result.node_count == 4
        assert result.edge_count == 4  # root->child1, root->child2, child1->final, child2->final
        
        # Verify all nodes are present
        node_names = [node.node_name for node in result.nodes]
        assert "root_node" in node_names
        assert "child1_node" in node_names
        assert "child2_node" in node_names
        assert "final_node" in node_names


@pytest.mark.asyncio
async def test_get_graph_structure_exception_handling():
    """Test exception handling in graph structure retrieval"""
    namespace = "test_namespace"
    run_id = "test_run_123"
    request_id = "test_request_123"
    
    with patch.object(State, 'find') as mock_find:
        mock_find.return_value.to_list = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await get_graph_structure(namespace, run_id, request_id)
