import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from exospherehost.statemanager import StateManager, TriggerState


def create_mock_aiohttp_session():
    """Helper function to create a properly mocked aiohttp session."""
    mock_session = AsyncMock()
    
    # Create mock response objects
    mock_post_response = AsyncMock()
    mock_get_response = AsyncMock()
    mock_put_response = AsyncMock()
    
    # Create mock context managers for each method
    mock_post_context = AsyncMock()
    mock_post_context.__aenter__.return_value = mock_post_response
    mock_post_context.__aexit__.return_value = None
    
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__.return_value = mock_get_response
    mock_get_context.__aexit__.return_value = None
    
    mock_put_context = AsyncMock()
    mock_put_context.__aenter__.return_value = mock_put_response
    mock_put_context.__aexit__.return_value = None
    
    # Set up the session methods to return the context managers using MagicMock
    mock_session.post = MagicMock(return_value=mock_post_context)
    mock_session.get = MagicMock(return_value=mock_get_context)
    mock_session.put = MagicMock(return_value=mock_put_context)
    
    # Set up session context manager
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    return mock_session, mock_post_response, mock_get_response, mock_put_response


@pytest.fixture
def state_manager_config():
    return {
        "namespace": "test_namespace",
        "state_manager_uri": "http://localhost:8080",
        "key": "test_key",
        "state_manager_version": "v1"
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://localhost:8080")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "test_key")


class TestStateManagerInitialization:
    def test_state_manager_initialization_with_all_params(self, state_manager_config):
        sm = StateManager(**state_manager_config)
        assert sm._namespace == "test_namespace"
        assert sm._state_manager_uri == "http://localhost:8080"
        assert sm._key == "test_key"
        assert sm._state_manager_version == "v1"

    def test_state_manager_initialization_with_env_vars(self, mock_env_vars):
        sm = StateManager(namespace="test_namespace")
        assert sm._state_manager_uri == "http://localhost:8080"
        assert sm._key == "test_key"

    def test_state_manager_default_version(self, mock_env_vars):
        sm = StateManager(namespace="test_namespace")
        assert sm._state_manager_version == "v0"


class TestStateManagerEndpointConstruction:
    def test_get_trigger_state_endpoint(self, state_manager_config):
        sm = StateManager(**state_manager_config)
        endpoint = sm._get_trigger_state_endpoint("test_graph")
        expected = "http://localhost:8080/v1/namespace/test_namespace/graph/test_graph/trigger"
        assert endpoint == expected

    def test_get_upsert_graph_endpoint(self, state_manager_config):
        sm = StateManager(**state_manager_config)
        endpoint = sm._get_upsert_graph_endpoint("test_graph")
        expected = "http://localhost:8080/v1/namespace/test_namespace/graph/test_graph"
        assert endpoint == expected

    def test_get_get_graph_endpoint(self, state_manager_config):
        sm = StateManager(**state_manager_config)
        endpoint = sm._get_get_graph_endpoint("test_graph")
        expected = "http://localhost:8080/v1/namespace/test_namespace/graph/test_graph"
        assert endpoint == expected


class TestTriggerState:
    def test_trigger_state_creation(self):
        state = TriggerState(
            identifier="test_trigger",
            inputs={"key1": "value1", "key2": "value2"}
        )
        assert state.identifier == "test_trigger"
        assert state.inputs == {"key1": "value1", "key2": "value2"}

    def test_trigger_state_model_dump(self):
        state = TriggerState(
            identifier="test_trigger",
            inputs={"key": "value"}
        )
        dumped = state.model_dump()
        assert dumped == {
            "identifier": "test_trigger",
            "inputs": {"key": "value"}
        }


class TestStateManagerTrigger:
    @pytest.mark.asyncio
    async def test_trigger_single_state_success(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"status": "success"})
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            state = TriggerState(identifier="test", inputs={"key": "value"})
            
            result = await sm.trigger("test_graph", inputs=state.inputs)
            
            assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_trigger_multiple_states_success(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"status": "success"})
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            states = [
                TriggerState(identifier="test1", inputs={"key1": "value1"}),
                TriggerState(identifier="test2", inputs={"key2": "value2"})
            ]
            
            merged_inputs = {**states[0].inputs, **states[1].inputs}
            result = await sm.trigger("test_graph", inputs=merged_inputs)
            
            assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_trigger_failure(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_post_response.status = 400
            mock_post_response.text = AsyncMock(return_value="Bad request")
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            state = TriggerState(identifier="test", inputs={"key": "value"})
            
            with pytest.raises(Exception, match="Failed to trigger state: 400 Bad request"):
                await sm.trigger("test_graph", inputs=state.inputs)


class TestStateManagerGetGraph:
    @pytest.mark.asyncio
    async def test_get_graph_success(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "VALID",
                "nodes": []
            })
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            result = await sm.get_graph("test_graph")
            
            assert result["name"] == "test_graph"
            assert result["validation_status"] == "VALID"

    @pytest.mark.asyncio
    async def test_get_graph_failure(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_get_response.status = 404
            mock_get_response.text = AsyncMock(return_value="Not found")
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            
            with pytest.raises(Exception, match="Failed to get graph: 404 Not found"):
                await sm.get_graph("test_graph")


class TestStateManagerUpsertGraph:
    @pytest.mark.asyncio
    async def test_upsert_graph_success_201(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class, \
             patch('exospherehost.statemanager.StateManager.get_graph') as mock_get_graph:
            
            # Mock the initial PUT response
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 201
            mock_put_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "PENDING"
            })
            
            mock_session_class.return_value = mock_session
            
            # Mock the polling responses
            mock_get_graph.side_effect = [
                {"validation_status": "PENDING"},
                {"validation_status": "VALID", "name": "test_graph"}
            ]
            
            sm = StateManager(**state_manager_config)
            graph_nodes = [{"name": "node1", "type": "test"}]
            secrets = {"secret1": "value1"}
            
            result = await sm.upsert_graph("test_graph", graph_nodes, secrets)
            
            assert result["validation_status"] == "VALID"
            assert result["name"] == "test_graph"

    @pytest.mark.asyncio
    async def test_upsert_graph_success_200(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class, \
             patch('exospherehost.statemanager.StateManager.get_graph') as mock_get_graph:
            
            # Mock the initial PUT response
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 200
            mock_put_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "VALID"
            })
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            graph_nodes = [{"name": "node1", "type": "test"}]
            secrets = {"secret1": "value1"}
            
            result = await sm.upsert_graph("test_graph", graph_nodes, secrets)
            
            assert result["validation_status"] == "VALID"
            # Should not call get_graph since status is already VALID
            mock_get_graph.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_graph_put_failure(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class:
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 500
            mock_put_response.text = AsyncMock(return_value="Internal server error")
            
            mock_session_class.return_value = mock_session
            
            sm = StateManager(**state_manager_config)
            graph_nodes = [{"name": "node1", "type": "test"}]
            secrets = {"secret1": "value1"}
            
            with pytest.raises(Exception, match="Failed to upsert graph: 500 Internal server error"):
                await sm.upsert_graph("test_graph", graph_nodes, secrets)

    @pytest.mark.asyncio
    async def test_upsert_graph_validation_timeout(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class, \
             patch('exospherehost.statemanager.StateManager.get_graph') as mock_get_graph:
            
            # Mock the initial PUT response
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 201
            mock_put_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "PENDING"
            })
            
            mock_session_class.return_value = mock_session
            
            # Mock the polling responses to always return PENDING
            mock_get_graph.return_value = {"validation_status": "PENDING"}
            
            sm = StateManager(**state_manager_config)
            graph_nodes = [{"name": "node1", "type": "test"}]
            secrets = {"secret1": "value1"}
            
            with pytest.raises(Exception, match="Graph validation check timed out after 1 seconds"):
                await sm.upsert_graph("test_graph", graph_nodes, secrets, validation_timeout=1, polling_interval=0.1) # type: ignore

    @pytest.mark.asyncio
    async def test_upsert_graph_validation_failed(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class, \
             patch('exospherehost.statemanager.StateManager.get_graph') as mock_get_graph:
            
            # Mock the initial PUT response
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 201
            mock_put_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "PENDING"
            })
            
            mock_session_class.return_value = mock_session
            
            # Mock the polling responses
            mock_get_graph.side_effect = [
                {"validation_status": "PENDING"},
                {
                    "validation_status": "INVALID",
                    "validation_errors": ["Node 'node1' not found"]
                }
            ]
            
            sm = StateManager(**state_manager_config)
            graph_nodes = [{"name": "node1", "type": "test"}]
            secrets = {"secret1": "value1"}
            
            with pytest.raises(Exception, match="Graph validation failed: INVALID and errors: \\[\"Node 'node1' not found\"\\]"):
                await sm.upsert_graph("test_graph", graph_nodes, secrets, validation_timeout=10, polling_interval=0.1) # type: ignore

    @pytest.mark.asyncio
    async def test_upsert_graph_custom_timeout_and_polling(self, state_manager_config):
        with patch('exospherehost.statemanager.aiohttp.ClientSession') as mock_session_class, \
             patch('exospherehost.statemanager.StateManager.get_graph') as mock_get_graph:
            
            # Mock the initial PUT response
            mock_session, mock_post_response, mock_get_response, mock_put_response = create_mock_aiohttp_session()
            
            mock_put_response.status = 201
            mock_put_response.json = AsyncMock(return_value={
                "name": "test_graph",
                "validation_status": "PENDING"
            })
            
            mock_session_class.return_value = mock_session
            
            # Mock the polling responses
            mock_get_graph.side_effect = [
                {"validation_status": "PENDING"},
                {"validation_status": "VALID", "name": "test_graph"}
            ]
            
            sm = StateManager(**state_manager_config)
            graph_nodes = [{"name": "node1", "type": "test"}]
            secrets = {"secret1": "value1"}
            
            result = await sm.upsert_graph(
                "test_graph", 
                graph_nodes, 
                secrets, 
                validation_timeout=30, 
                polling_interval=2
            )
            
            assert result["validation_status"] == "VALID" 