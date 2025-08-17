import pytest
import asyncio
from exospherehost.statemanager import StateManager, TriggerState


def test_trigger_requires_either_state_or_states(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	sm = StateManager(namespace="ns")
	with pytest.raises(ValueError):
		asyncio.run(sm.trigger("g"))


def test_trigger_rejects_both_state_and_states(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	sm = StateManager(namespace="ns")
	state = TriggerState(identifier="id", inputs={})
	with pytest.raises(ValueError):
		asyncio.run(sm.trigger("g", state=state, states=[state]))


def test_trigger_rejects_empty_states_list(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	sm = StateManager(namespace="ns")
	with pytest.raises(ValueError):
		asyncio.run(sm.trigger("g", states=[]))