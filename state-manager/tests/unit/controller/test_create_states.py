import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from beanie import PydanticObjectId
from datetime import datetime

from app.controller.create_states import create_states, get_node_template
from app.models.create_models import CreateRequestModel, RequestStateModel
from app.models.state_status_enum import StateStatusEnum
from app.models.node_template_model import NodeTemplate


class TestGetNodeTemplate:
    """Test cases for get_node_template function"""

    def test_get_node_template_success(self):
        """Test successful retrieval of node template"""
        # Arrange
        mock_node = NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="test_identifier",
            inputs={},
            next_nodes=[],
            unites=None
        )
        mock_graph_template = MagicMock()
        mock_graph_template.get_node_by_identifier.return_value = mock_node

        # Act
        result = get_node_template(mock_graph_template, "test_identifier")

        # Assert
        assert result == mock_node
        mock_graph_template.get_node_by_identifier.assert_called_once_with("test_identifier")

    def test_get_node_template_not_found(self):
        """Test when node template is not found"""
        # Arrange
        mock_graph_template = MagicMock()
        mock_graph_template.get_node_by_identifier.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_node_template(mock_graph_template, "non_existent_identifier")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Node template not found"


class TestCreateStates:
    """Test cases for create_states function"""

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_graph_name(self):
        return "test_graph"

    @pytest.fixture
    def mock_node_template(self):
        return NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="test_identifier",
            inputs={},
            next_nodes=[],
            unites=None
        )

    @pytest.fixture
    def mock_graph_template(self, mock_node_template, mock_graph_name, mock_namespace):
        mock_template = MagicMock()
        mock_template.name = mock_graph_name
        mock_template.namespace = mock_namespace
        mock_template.get_node_by_identifier.return_value = mock_node_template
        return mock_template

    @pytest.fixture
    def mock_create_request(self):
        return CreateRequestModel(
            run_id="test_run_id",
            states=[
                RequestStateModel(
                    identifier="test_identifier",
                    inputs={"key": "value"}
                )
            ]
        )

    @pytest.fixture
    def mock_state(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.identifier = "test_identifier"
        state.node_name = "test_node"
        state.run_id = "test_run_id"
        state.graph_name = "test_graph"
        state.inputs = {"key": "value"}
        state.created_at = datetime.now()
        return state

    @patch('app.controller.create_states.GraphTemplate')
    @patch('app.controller.create_states.State')
    async def test_create_states_success(
        self, 
        mock_state_class,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_create_request,
        mock_graph_template,
        mock_state,
        mock_request_id
    ):
        """Test successful creation of states"""
        # Arrange
        # Mock the GraphTemplate class and its find_one method
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        # Mock State.insert_many
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_ids = [PydanticObjectId()]
        mock_state_class.insert_many = AsyncMock(return_value=mock_insert_result)
        
        # Mock State.find().to_list()
        mock_state_find = MagicMock()
        mock_state_find.to_list = AsyncMock(return_value=[mock_state])
        mock_state_class.find = MagicMock(return_value=mock_state_find)        

        # Act
        result = await create_states(
            mock_namespace, 
            mock_graph_name, 
            mock_create_request, 
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.CREATED
        assert len(result.states) == 1
        assert result.states[0].identifier == "test_identifier"
        assert result.states[0].node_name == "test_node"
        assert result.states[0].inputs == {"key": "value"}
        
        # Verify find_one was called (with any arguments)
        assert mock_graph_template_class.find_one.called
        mock_state_class.insert_many.assert_called_once()
        mock_state_class.find.assert_called_once()

    @patch('app.controller.create_states.GraphTemplate')
    async def test_create_states_graph_template_not_found(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_create_request,
        mock_request_id
    ):
        """Test when graph template is not found"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_states(
                mock_namespace, 
                mock_graph_name, 
                mock_create_request, 
                mock_request_id
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Graph template not found"
        assert mock_graph_template_class.find_one.called

    @patch('app.controller.create_states.GraphTemplate')
    async def test_create_states_node_template_not_found(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_create_request,
        mock_request_id
    ):
        """Test when node template is not found in graph template"""
        # Arrange
        mock_graph_template = MagicMock()
        mock_graph_template.get_node_by_identifier.return_value = None
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_states(
                mock_namespace, 
                mock_graph_name, 
                mock_create_request, 
                mock_request_id
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Node template not found"
        assert mock_graph_template_class.find_one.called

    @patch('app.controller.create_states.GraphTemplate')
    async def test_create_states_database_error(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_create_request,
        mock_graph_template,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await create_states(
                mock_namespace, 
                mock_graph_name, 
                mock_create_request, 
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"
        assert mock_graph_template_class.find_one.called

    @patch('app.controller.create_states.GraphTemplate')
    @patch('app.controller.create_states.State')
    async def test_create_states_multiple_states(
        self,
        mock_state_class,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_graph_template,
        mock_request_id
    ):
        """Test creation of multiple states"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_ids = [PydanticObjectId(), PydanticObjectId()]
        mock_state_class.insert_many = AsyncMock(return_value=mock_insert_result)
        
        # Mock State.find().to_list() for multiple states
        mock_state1 = MagicMock()
        mock_state1.id = PydanticObjectId()
        mock_state1.identifier = "node1"
        mock_state1.node_name = "test_node"
        mock_state1.run_id = "test_run_id"
        mock_state1.graph_name = "test_graph"
        mock_state1.inputs = {"input1": "value1"}
        mock_state1.created_at = datetime.now()
        
        mock_state2 = MagicMock()
        mock_state2.id = PydanticObjectId()
        mock_state2.identifier = "node2"
        mock_state2.node_name = "test_node"
        mock_state2.run_id = "test_run_id"
        mock_state2.graph_name = "test_graph"
        mock_state2.inputs = {"input2": "value2"}
        mock_state2.created_at = datetime.now()
        
        mock_state_find = MagicMock()
        mock_state_find.to_list = AsyncMock(return_value=[mock_state1, mock_state2])
        mock_state_class.find = MagicMock(return_value=mock_state_find)

        create_request = CreateRequestModel(
            run_id="test_run_id",
            states=[
                RequestStateModel(identifier="node1", inputs={"input1": "value1"}),
                RequestStateModel(identifier="node2", inputs={"input2": "value2"})
            ]
        )

        # Act
        result = await create_states(
            mock_namespace, 
            mock_graph_name, 
            create_request, 
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.CREATED
        assert mock_graph_template_class.find_one.called
        mock_state_class.insert_many.assert_called_once()
        # Verify that insert_many was called with 2 states
        call_args = mock_state_class.insert_many.call_args[0][0]
        assert len(call_args) == 2
