from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.controller.create_states import trigger_graph
from app.models.create_models import TriggerGraphRequestModel, RequestStateModel, ResponseStateModel
from app.models.state_status_enum import StateStatusEnum


@pytest.fixture
def mock_request():
    return TriggerGraphRequestModel(
        states=[
            RequestStateModel(
                identifier="test_node_1",
                inputs={"input1": "value1"}
            ),
            RequestStateModel(
                identifier="test_node_2", 
                inputs={"input2": "value2"}
            )
        ]
    )


@pytest.mark.asyncio
async def test_trigger_graph_success(mock_request):
    """Test successful graph triggering"""
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"
    
    # Mock the create_states function
    with patch('app.controller.create_states.create_states') as mock_create_states:
        mock_response = MagicMock()
        mock_response.status = StateStatusEnum.CREATED
        mock_response.states = [
            ResponseStateModel(
                state_id="state_1",
                identifier="test_node_1",
                node_name="TestNode1",
                graph_name=graph_name,
                run_id="generated_run_id",
                inputs={"input1": "value1"},
                created_at=datetime(2024, 1, 1, 0, 0, 0)
            ),
            ResponseStateModel(
                state_id="state_2",
                identifier="test_node_2",
                node_name="TestNode2", 
                graph_name=graph_name,
                run_id="generated_run_id",
                inputs={"input2": "value2"},
                created_at=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        mock_create_states.return_value = mock_response
        
        # Call the function
        result = await trigger_graph(namespace_name, graph_name, mock_request, x_exosphere_request_id)
        
        # Verify the result
        assert result.run_id is not None
        assert result.status == StateStatusEnum.CREATED
        assert len(result.states) == 2
        assert result.states[0].identifier == "test_node_1"
        assert result.states[1].identifier == "test_node_2"
        
        # Verify create_states was called with the correct parameters
        mock_create_states.assert_called_once()
        call_args = mock_create_states.call_args
        assert call_args[0][0] == namespace_name  # namespace_name
        assert call_args[0][1] == graph_name      # graph_name
        assert call_args[0][3] == x_exosphere_request_id  # x_exosphere_request_id
        
        # Verify the CreateRequestModel was created with a generated run_id
        create_request = call_args[0][2]  # body parameter
        assert create_request.run_id is not None
        assert create_request.states == mock_request.states


@pytest.mark.asyncio
async def test_trigger_graph_create_states_error(mock_request):
    """Test error handling when create_states fails"""
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"
    
    # Mock create_states to raise an exception
    with patch('app.controller.create_states.create_states') as mock_create_states:
        mock_create_states.side_effect = HTTPException(status_code=404, detail="Graph template not found")
        
        # Call the function and expect it to raise the same exception
        with pytest.raises(HTTPException) as exc_info:
            await trigger_graph(namespace_name, graph_name, mock_request, x_exosphere_request_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Graph template not found"
