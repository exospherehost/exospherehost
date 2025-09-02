import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException

from app.controller.trigger_graph import trigger_graph
from app.models.trigger_model import TriggerGraphRequestModel
from app.models.state_status_enum import StateStatusEnum


@pytest.fixture
def mock_request():
    return TriggerGraphRequestModel(
        store={"k1": "v1"},
        inputs={"input1": "value1"}
    )


@pytest.mark.asyncio
async def test_trigger_graph_success(mock_request):
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"

    with patch('app.controller.trigger_graph.GraphTemplate') as mock_graph_template_cls, \
         patch('app.controller.trigger_graph.Store') as mock_store_cls, \
         patch('app.controller.trigger_graph.State') as mock_state_cls, \
         patch('app.controller.trigger_graph.Run') as mock_run_cls:

        mock_graph_template = MagicMock()
        mock_graph_template.is_valid.return_value = True
        mock_root_node = MagicMock()
        mock_root_node.node_name = "root_node"
        mock_root_node.identifier = "root_id"
        mock_root_node.inputs = {"input1": "default"}
        mock_graph_template.get_root_node.return_value = mock_root_node
        mock_graph_template_cls.get = AsyncMock(return_value=mock_graph_template)

        mock_store_cls.insert_many = AsyncMock(return_value=None)
        mock_state_instance = MagicMock()
        mock_state_instance.insert = AsyncMock(return_value=None)
        mock_state_cls.return_value = mock_state_instance
        
        mock_run_instance = MagicMock()
        mock_run_instance.insert = AsyncMock(return_value=None)
        mock_run_cls.return_value = mock_run_instance

        result = await trigger_graph(namespace_name, graph_name, mock_request, x_exosphere_request_id)

        assert result.status == StateStatusEnum.CREATED
        assert isinstance(result.run_id, str) and len(result.run_id) > 0

        mock_graph_template_cls.get.assert_awaited_once_with(namespace_name, graph_name)
        mock_store_cls.insert_many.assert_awaited_once()
        mock_state_instance.insert.assert_awaited_once()


@pytest.mark.asyncio
async def test_trigger_graph_graph_template_not_found(mock_request):
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"

    with patch('app.controller.trigger_graph.GraphTemplate') as mock_graph_template_cls:
        mock_graph_template_cls.get = AsyncMock(side_effect=ValueError("Graph template not found"))

        with pytest.raises(HTTPException) as exc_info:
            await trigger_graph(namespace_name, graph_name, mock_request, x_exosphere_request_id)

        assert exc_info.value.status_code == 404
        assert "Graph template not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_trigger_graph_invalid_graph_template(mock_request):
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"

    with patch('app.controller.trigger_graph.GraphTemplate') as mock_graph_template_cls:
        mock_graph_template = MagicMock()
        mock_graph_template.is_valid.return_value = False
        mock_graph_template_cls.get = AsyncMock(return_value=mock_graph_template)

        with pytest.raises(HTTPException) as exc_info:
            await trigger_graph(namespace_name, graph_name, mock_request, x_exosphere_request_id)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Graph template is not valid"


@pytest.mark.asyncio
async def test_trigger_graph_missing_store_keys():
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"

    req = TriggerGraphRequestModel(store={}, inputs={})

    with patch('app.controller.trigger_graph.GraphTemplate') as mock_graph_template_cls:
        mock_graph_template = MagicMock()
        mock_graph_template.is_valid.return_value = True
        mock_graph_template.store_config.required_keys = ["k1"]
        mock_root_node = MagicMock()
        mock_root_node.node_name = "root_node"
        mock_root_node.identifier = "root_id"
        mock_graph_template.get_root_node.return_value = mock_root_node
        mock_graph_template_cls.get = AsyncMock(return_value=mock_graph_template)

        with pytest.raises(HTTPException) as exc_info:
            await trigger_graph(namespace_name, graph_name, req, x_exosphere_request_id)

        assert exc_info.value.status_code == 400
        assert "Missing store keys" in exc_info.value.detail


@pytest.mark.asyncio
async def test_trigger_graph_value_error_not_graph_template_not_found(mock_request):
    """Test trigger_graph handles ValueError that is not about graph template not found"""
    namespace_name = "test_namespace"
    graph_name = "test_graph"
    x_exosphere_request_id = "test_request_id"

    with patch('app.controller.trigger_graph.GraphTemplate') as mock_graph_template_cls:
        # Simulate a ValueError that doesn't contain "Graph template not found"
        mock_graph_template_cls.get.side_effect = ValueError("Some other validation error")
        
        with pytest.raises(ValueError, match="Some other validation error"):
            await trigger_graph(namespace_name, graph_name, mock_request, x_exosphere_request_id)
