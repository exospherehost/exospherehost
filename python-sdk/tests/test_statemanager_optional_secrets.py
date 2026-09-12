"""
Regression for https://github.com/FailproofAI/runtime/issues/631.

A graph that needs no secrets should be creatable without the caller passing an empty
mapping. The state manager's upsert request requires the `secrets` field, and
`GraphTemplate.set_secrets` replaces the stored secrets on every upsert, so the SDK sends
an empty mapping when the argument is omitted and never mutates a caller's own mapping.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from exospherehost.models import GraphNodeModel
from exospherehost.statemanager import StateManager


NODES = [GraphNodeModel(node_name="n", namespace="demo", identifier="n", inputs={}, next_nodes=None, unites=None)]


def _session(status=201):
    session = AsyncMock()
    response = AsyncMock()
    response.status = status
    response.json = AsyncMock(return_value={"name": "g", "validation_status": "VALID"})
    context = AsyncMock()
    context.__aenter__.return_value = response
    context.__aexit__.return_value = None
    session.put = MagicMock(return_value=context)
    session.__aenter__.return_value = session
    session.__aexit__.return_value = None
    return session


def _sent_body(session):
    return session.put.call_args.kwargs["json"]


@pytest.mark.asyncio
async def test_secrets_can_be_omitted_and_an_empty_mapping_is_sent():
    session = _session()
    with patch("exospherehost.statemanager.aiohttp.ClientSession", return_value=session):
        sm = StateManager("demo", state_manager_uri="http://sm", key="k")
        result = await sm.upsert_graph("g", NODES)
    assert result["validation_status"] == "VALID"
    assert _sent_body(session)["secrets"] == {}


@pytest.mark.asyncio
async def test_explicit_secrets_are_sent_unchanged_and_the_caller_mapping_is_not_mutated():
    session = _session()
    secrets = {"TOKEN": "synthetic-value"}
    snapshot = dict(secrets)
    with patch("exospherehost.statemanager.aiohttp.ClientSession", return_value=session):
        sm = StateManager("demo", state_manager_uri="http://sm", key="k")
        await sm.upsert_graph("g", NODES, secrets)
    assert _sent_body(session)["secrets"] == snapshot
    assert _sent_body(session)["secrets"] is not secrets
    assert secrets == snapshot


@pytest.mark.asyncio
async def test_repeated_calls_without_secrets_share_no_mutable_default():
    session = _session()
    with patch("exospherehost.statemanager.aiohttp.ClientSession", return_value=session):
        sm = StateManager("demo", state_manager_uri="http://sm", key="k")
        await sm.upsert_graph("g", NODES)
        first = _sent_body(session)["secrets"]
        first["LEAKED"] = "x"
        await sm.upsert_graph("g", NODES)
        second = _sent_body(session)["secrets"]
    assert second == {}
    assert second is not first


@pytest.mark.asyncio
async def test_positional_secrets_still_bind_to_the_third_parameter():
    session = _session()
    with patch("exospherehost.statemanager.aiohttp.ClientSession", return_value=session):
        sm = StateManager("demo", state_manager_uri="http://sm", key="k")
        await sm.upsert_graph("g", NODES, {"A": "1"}, None, None, None, 5, 1)
    assert _sent_body(session)["secrets"] == {"A": "1"}
