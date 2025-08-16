import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from datetime import datetime

from app.controller.get_graph_template import get_graph_template
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.node_template_model import NodeTemplate


class TestGetGraphTemplate:
    """Test cases for get_graph_template function"""

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
    def mock_graph_template(self):
        template = MagicMock()
        template.nodes = [
            NodeTemplate(
                identifier="node1",
                node_name="Test Node 1",
                namespace="test_namespace",
                inputs={},
                next_nodes=[],
                unites=None
            ),
            NodeTemplate(
                identifier="node2",
                node_name="Test Node 2",
                namespace="test_namespace",
                inputs={},
                next_nodes=[],
                unites=None
            )
        ]
        template.validation_status = GraphTemplateValidationStatus.VALID
        template.validation_errors = []
        template.secrets = {"secret1": "encrypted_value1", "secret2": "encrypted_value2"}
        template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        template.get_secrets.return_value = {"secret1": "encrypted_value1", "secret2": "encrypted_value2"}
        return template

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_success(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_graph_template,
        mock_request_id
    ):
        """Test successful retrieval of graph template"""
        # Arrange        
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)

        # Act
        result = await get_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_request_id
        )

        # Assert
        assert result.validation_status == GraphTemplateValidationStatus.VALID
        assert result.validation_errors == []
        assert result.secrets == {"secret1": True, "secret2": True}
        assert result.created_at == mock_graph_template.created_at
        assert result.updated_at == mock_graph_template.updated_at
        
        mock_graph_template_class.find_one.assert_called_once()

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_not_found(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_request_id
    ):
        """Test when graph template is not found"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_graph_template(
                mock_namespace,
                mock_graph_name,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == f"Graph template {mock_graph_name} not found in namespace {mock_namespace}"

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_with_validation_errors(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_request_id
    ):
        """Test retrieval of graph template with validation errors"""
        # Arrange
        template = MagicMock()
        template.nodes = [NodeTemplate(
            identifier="node1",
            node_name="Test Node",
            namespace="test_namespace",
            inputs={},
            next_nodes=[],
            unites=None
        )]
        template.validation_status = GraphTemplateValidationStatus.INVALID
        template.validation_errors = ["Error 1", "Error 2"]
        template.secrets = {"secret1": "encrypted_value1"}
        template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        template.get_secrets.return_value = {"secret1": "encrypted_value1"}
        
        mock_graph_template_class.find_one = AsyncMock(return_value=template)

        # Act
        result = await get_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_request_id
        )

        # Assert
        assert result.validation_status == GraphTemplateValidationStatus.INVALID
        assert result.validation_errors == ["Error 1", "Error 2"]
        assert result.secrets == {"secret1": True}

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_with_pending_validation(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_request_id
    ):
        """Test retrieval of graph template with pending validation"""
        # Arrange
        template = MagicMock()
        template.nodes = [NodeTemplate(
            identifier="node1",
            node_name="Test Node",
            namespace="test_namespace",
            inputs={},
            next_nodes=[],
            unites=None
        )]
        template.validation_status = GraphTemplateValidationStatus.PENDING
        template.validation_errors = []
        template.secrets = {}
        template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        template.get_secrets.return_value = {}
        
        mock_graph_template_class.find_one = AsyncMock(return_value=template)

        # Act
        result = await get_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_request_id
        )

        # Assert
        assert result.validation_status == GraphTemplateValidationStatus.PENDING
        assert result.validation_errors == []
        assert result.secrets == {}

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_with_empty_nodes(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_request_id
    ):
        """Test retrieval of graph template with empty nodes"""
        # Arrange
        template = MagicMock()
        template.nodes = []
        template.validation_status = GraphTemplateValidationStatus.VALID
        template.validation_errors = []
        template.secrets = {}
        template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        template.get_secrets.return_value = {}
        
        mock_graph_template_class.find_one = AsyncMock(return_value=template)

        # Act
        result = await get_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_request_id
        )

        # Assert
        assert result.nodes == []
        assert result.validation_status == GraphTemplateValidationStatus.VALID
        assert result.secrets == {}

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_database_error(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await get_graph_template(
                mock_namespace,
                mock_graph_name,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.get_graph_template.GraphTemplate')
    async def test_get_graph_template_with_complex_secrets(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_request_id
    ):
        """Test retrieval of graph template with complex secrets structure"""
        # Arrange
        template = MagicMock()
        template.nodes = [NodeTemplate(
            identifier="node1",
            node_name="Test Node",
            namespace="test_namespace",
            inputs={},
            next_nodes=[],
            unites=None
        )]
        template.validation_status = GraphTemplateValidationStatus.VALID
        template.validation_errors = []
        template.secrets = {
            "api_key": "encrypted_api_key",
            "database_url": "encrypted_db_url",
            "aws_credentials": "encrypted_aws_creds"
        }
        template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        template.get_secrets.return_value = {
            "api_key": "encrypted_api_key",
            "database_url": "encrypted_db_url",
            "aws_credentials": "encrypted_aws_creds"
        }
        
        mock_graph_template_class.find_one = AsyncMock(return_value=template)

        # Act
        result = await get_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_request_id
        )

        # Assert
        expected_secrets = {
            "api_key": True,
            "database_url": True,
            "aws_credentials": True
        }
        assert result.secrets == expected_secrets

