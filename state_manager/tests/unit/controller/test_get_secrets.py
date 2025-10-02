import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from beanie import PydanticObjectId

from app.controller.get_secrets import get_secrets
from app.models.secrets_response import SecretsResponseModel


class TestGetSecrets:
    """Test cases for get_secrets function"""

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
    def mock_state(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.namespace_name = "test_namespace"
        state.graph_name = "test_graph"
        return state

    @pytest.fixture
    def mock_graph_template(self):
        template = MagicMock()
        template.get_secrets.return_value = {
            "api_key": "encrypted_api_key",
            "database_url": "encrypted_db_url"
        }
        return template

    @patch('app.controller.get_secrets.State')
    @patch('app.controller.get_secrets.GraphTemplate')
    async def test_get_secrets_success(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_graph_template,
        mock_request_id
    ):
        """Test successful retrieval of secrets"""
        # Arrange
        mock_state_class.get = AsyncMock(return_value=mock_state)
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)

        # Act
        result = await get_secrets(
            mock_namespace,
            mock_state_id,
            mock_request_id
        )

        # Assert
        assert isinstance(result, SecretsResponseModel)
        assert result.secrets == {
            "api_key": "encrypted_api_key",
            "database_url": "encrypted_db_url"
        }
        
        mock_state_class.get.assert_called_once_with(mock_state_id)
        mock_graph_template_class.find_one.assert_called_once()

    @patch('app.controller.get_secrets.State')
    async def test_get_secrets_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_request_id
    ):
        """Test when state is not found"""
        # Arrange
        mock_state_class.get = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await get_secrets(
                mock_namespace,
                mock_state_id,
                mock_request_id
            )
        
        assert str(exc_info.value) == f"State {mock_state_id} not found"

    @patch('app.controller.get_secrets.State')
    async def test_get_secrets_namespace_mismatch(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_request_id
    ):
        """Test when state belongs to different namespace"""
        # Arrange
        mock_state = MagicMock()
        mock_state.namespace_name = "different_namespace"
        mock_state_class.get = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await get_secrets(
                mock_namespace,
                mock_state_id,
                mock_request_id
            )
        
        assert str(exc_info.value) == f"State {mock_state_id} does not belong to namespace {mock_namespace}"

    @patch('app.controller.get_secrets.State')
    @patch('app.controller.get_secrets.GraphTemplate')
    async def test_get_secrets_graph_template_not_found(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_request_id
    ):
        """Test when graph template is not found"""
        # Arrange
        mock_state_class.get = AsyncMock(return_value=mock_state)
        mock_graph_template_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await get_secrets(
                mock_namespace,
                mock_state_id,
                mock_request_id
            )
        
        assert str(exc_info.value) == f"Graph template {mock_state.graph_name} not found in namespace {mock_namespace}"

    @patch('app.controller.get_secrets.State')
    @patch('app.controller.get_secrets.GraphTemplate')
    async def test_get_secrets_empty_secrets(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_request_id
    ):
        """Test retrieval when graph template has no secrets"""
        # Arrange
        mock_state_class.get = AsyncMock(return_value=mock_state)
        
        template = MagicMock()
        template.get_secrets.return_value = {}
        mock_graph_template_class.find_one = AsyncMock(return_value=template)

        # Act
        result = await get_secrets(
            mock_namespace,
            mock_state_id,
            mock_request_id
        )

        # Assert
        assert isinstance(result, SecretsResponseModel)
        assert result.secrets == {}

    @patch('app.controller.get_secrets.State')
    @patch('app.controller.get_secrets.GraphTemplate')
    async def test_get_secrets_complex_secrets(
        self,
        mock_graph_template_class,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_request_id
    ):
        """Test retrieval of complex secrets structure"""
        # Arrange
        mock_state_class.get = AsyncMock(return_value=mock_state)
        
        template = MagicMock()
        template.get_secrets.return_value = {
            "aws_access_key": "encrypted_aws_key",
            "aws_secret_key": "encrypted_aws_secret",
            "database_password": "encrypted_db_password",
            "api_token": "encrypted_api_token",
            "ssl_certificate": "encrypted_ssl_cert"
        }
        mock_graph_template_class.find_one = AsyncMock(return_value=template)

        # Act
        result = await get_secrets(
            mock_namespace,
            mock_state_id,
            mock_request_id
        )

        # Assert
        expected_secrets = {
            "aws_access_key": "encrypted_aws_key",
            "aws_secret_key": "encrypted_aws_secret",
            "database_password": "encrypted_db_password",
            "api_token": "encrypted_api_token",
            "ssl_certificate": "encrypted_ssl_cert"
        }
        assert result.secrets == expected_secrets

    @patch('app.controller.get_secrets.State')
    async def test_get_secrets_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.get = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await get_secrets(
                mock_namespace,
                mock_state_id,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"