import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from exospherehost.models import (
    GraphNodeModel,
    UnitesModel,
    UnitesStrategyEnum,
    StoreConfigModel,
    RetryPolicyModel,
)
from exospherehost.statemanager import StateManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_session_with_status(status: int, json_payload: dict):
    """Create an aiohttp-like mock ClientSession returning the given status & payload."""
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=json_payload)

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    # route all verbs to the same context manager
    mock_session.post.return_value = mock_ctx
    mock_session.get.return_value = mock_ctx
    mock_session.put.return_value = mock_ctx

    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    return mock_session, mock_resp


# ---------------------------------------------------------------------------
# GraphNodeModel & related validation
# ---------------------------------------------------------------------------

def test_graph_node_model_trimming_and_defaults():
    model = GraphNodeModel(
        node_name="  MyNode  ",
        namespace="ns",
        identifier="  node1  ",
        inputs={},
        next_nodes=["  next1  "],
        unites=UnitesModel(identifier="  unite1  ")  # strategy default should kick in
    )

    # Fields should be stripped
    assert model.node_name == "MyNode"
    assert model.identifier == "node1"
    assert model.next_nodes == ["next1"]
    assert model.unites is not None
    assert model.unites.identifier == "unite1"
    # Default enum value check
    assert model.unites.strategy == UnitesStrategyEnum.ALL_SUCCESS


@pytest.mark.parametrize(
    "field, kwargs, err_msg",
    [
        ("node_name", {"node_name": "  "}, "Node name cannot be empty"),
        ("identifier", {"identifier": "store"}, "reserved word"),
        (
            "next_nodes",
            {"next_nodes": ["", "id2"]},
            "cannot be empty",
        ),
        (
            "next_nodes",
            {"next_nodes": ["dup", "dup"]},
            "not unique",
        ),
        (
            "unites",
            {"unites": UnitesModel(identifier="  ")},
            "Unites identifier cannot be empty",
        ),
    ],
)
def test_graph_node_model_invalid(field, kwargs, err_msg):
    base_kwargs = dict(
        node_name="n",
        namespace="ns",
        identifier="id1",
        inputs={},
        next_nodes=None,
        unites=None
    )
    base_kwargs.update(kwargs)
    with pytest.raises(ValueError) as e:
        GraphNodeModel(**base_kwargs) # type: ignore
    assert err_msg in str(e.value)


# ---------------------------------------------------------------------------
# StoreConfigModel validation
# ---------------------------------------------------------------------------

def test_store_config_model_valid_and_normalises():
    cfg = StoreConfigModel(
        required_keys=["  a ", "b"],
        default_values={" c ": "1", "d": "2"},
    )
    # Keys should be trimmed and values stringified
    assert cfg.required_keys == ["a", "b"]
    assert cfg.default_values == {"c": "1", "d": "2"}


@pytest.mark.parametrize(
    "kwargs, msg",
    [
        ({"required_keys": ["a", "a"]}, "duplicated"),
        ({"required_keys": ["a."]}, "cannot contain '.'"),
        ({"required_keys": ["  "]}, "cannot be empty"),
        ({"default_values": {"k.k": "v"}}, "cannot contain '.'"),
        ({"default_values": {"": "v"}}, "cannot be empty"),
    ],
)
def test_store_config_model_invalid(kwargs, msg):
    with pytest.raises(ValueError) as e:
        StoreConfigModel(**kwargs)
    assert msg in str(e.value)





# ---------------------------------------------------------------------------
# RetryPolicyModel defaults (simple smoke test)
# ---------------------------------------------------------------------------

def test_retry_policy_defaults():
    pol = RetryPolicyModel()
    assert pol.max_retries == 3
    assert pol.backoff_factor == 2000
    # Ensure all enum values round-trip via model_dump
    dumped = pol.model_dump()
    assert dumped["strategy"] == pol.strategy


# ---------------------------------------------------------------------------
# StateManager – store_config / store handling logic
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_statemanager_upsert_includes_store_config(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    sm = StateManager(namespace="ns")

    node = GraphNodeModel(node_name="n", namespace="ns", identifier="id1", inputs={}, next_nodes=None, unites=None) # type: ignore
    store_cfg = StoreConfigModel(required_keys=["k1"], default_values={"k2": "v"})

    # Mock ClientSession
    mock_session, _ = _make_mock_session_with_status(201, {"validation_status": "VALID"})

    with patch("exospherehost.statemanager.aiohttp.ClientSession", return_value=mock_session):
        await sm.upsert_graph("g", [node], secrets={}, store_config=store_cfg)

    mock_session.put.assert_called_once()
    _, kwargs = mock_session.put.call_args
    # Ensure the store_config is present and exactly what model_dump produced
    assert "store_config" in kwargs["json"]
    assert kwargs["json"]["store_config"] == store_cfg.model_dump()


@pytest.mark.asyncio
async def test_statemanager_trigger_passes_store(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    sm = StateManager(namespace="ns")

    mock_session, _ = _make_mock_session_with_status(200, {})

    with patch("exospherehost.statemanager.aiohttp.ClientSession", return_value=mock_session):
        await sm.trigger("g", inputs={"a": "1"}, store={"cursor": "0"}, start_delay=123)

    mock_session.post.assert_called_once()
    _, kwargs = mock_session.post.call_args
    assert kwargs["json"] == {"inputs": {"a": "1"}, "store": {"cursor": "0"}, "start_delay": 123} 