"""
Regression for https://github.com/FailproofAI/runtime/issues/642.

A state manager URI configured with a trailing slash ("http://localhost:8000/") produced
endpoints with a doubled separator ("http://localhost:8000//v0/..."), which some servers
and proxies reject. The base must be normalised once, after the environment fallback, so
explicit and environment configuration behave the same and every endpoint helper agrees.
"""
import pytest

from exospherehost.statemanager import StateManager


BASES = [
    # (configured base, expected normalised base)
    ("http://localhost:8000/", "http://localhost:8000"),
    ("http://localhost:8000", "http://localhost:8000"),
    ("https://example.test/", "https://example.test"),
    ("https://example.test/api/", "https://example.test/api"),
    ("https://example.test/api", "https://example.test/api"),
    ("http://[::1]:8000/", "http://[::1]:8000"),
    ("https://example.test///", "https://example.test"),
]

ENDPOINTS = [
    ("_get_trigger_state_endpoint", "/v0/namespace/demo/graph/g/trigger"),
    ("_get_upsert_graph_endpoint", "/v0/namespace/demo/graph/g"),
    ("_get_get_graph_endpoint", "/v0/namespace/demo/graph/g"),
]


@pytest.mark.parametrize("configured, normalised", BASES)
@pytest.mark.parametrize("helper, suffix", ENDPOINTS)
def test_explicit_base_uri_has_one_separator_before_the_version(configured, normalised, helper, suffix):
    sm = StateManager("demo", state_manager_uri=configured, key="k")
    assert getattr(sm, helper)("g") == normalised + suffix


@pytest.mark.parametrize("configured, normalised", BASES)
@pytest.mark.parametrize("helper, suffix", ENDPOINTS)
def test_environment_base_uri_is_normalised_the_same_way(monkeypatch, configured, normalised, helper, suffix):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", configured)
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
    sm = StateManager("demo")
    assert getattr(sm, helper)("g") == normalised + suffix


def test_a_missing_base_uri_stays_missing(monkeypatch):
    # Normalisation must not turn an unset URI into a valid-looking string.
    monkeypatch.delenv("EXOSPHERE_STATE_MANAGER_URI", raising=False)
    sm = StateManager("demo", key="k")
    assert sm._state_manager_uri is None
