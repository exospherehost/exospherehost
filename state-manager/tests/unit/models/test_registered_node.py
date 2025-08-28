# Framework/Library note:
# - Testing framework: pytest
# - Async support: pytest-asyncio (function-level @pytest.mark.asyncio)
# These tests focus on RegisteredNode's validation, indexes, and async query methods.

import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock

# Prefer canonical import; fallback to dynamic import if package layout differs.
try:
    from state_manager.models.registered_node import RegisteredNode
except Exception:
    # Dynamic fallback: locate a registered_node.py exposing RegisteredNode
    import importlib.util
    import sys
    from pathlib import Path

    def _import_registered_node() -> type:
        # Search up to repo root for a file named registered_node.py that defines RegisteredNode
        start = Path(__file__).resolve()
        roots = list(start.parents)[:6]  # limit search depth
        for root in roots:
            for path in root.rglob("registered_node.py"):
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    if "class RegisteredNode" not in text:
                        continue
                    mod_name = f"_rn_{abs(hash(str(path)))}"
                    spec = importlib.util.spec_from_file_location(mod_name, path)
                    if not spec or not spec.loader:
                        continue
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)  # type: ignore[attr-defined]
                    if hasattr(module, "RegisteredNode"):
                        return getattr(module, "RegisteredNode")
                except Exception:
                    continue
        raise ImportError("Could not import RegisteredNode via dynamic search.")
    RegisteredNode = _import_registered_node()

# Local lightweight stand-in for NodeTemplate to avoid coupling to its full schema.
class _DummyTemplate:
    def __init__(self, node_name: str, namespace: str) -> None:
        self.node_name = node_name
        self.namespace = namespace

def _valid_node_data():
    return {
        "name": "example-node",
        "namespace": "example-ns",
        "runtime_name": "rt",
        "runtime_namespace": "rt-ns",
        "inputs_schema": {"type": "object", "properties": {}},
        "outputs_schema": {"type": "object", "properties": {}},
        # 'secrets' intentionally omitted to verify default behavior
    }

@pytest.mark.parametrize(
    "missing_field",
    ["name", "namespace", "runtime_name", "runtime_namespace", "inputs_schema", "outputs_schema"],
)
def test_registered_node_required_fields_validation(missing_field):
    data = _valid_node_data()
    data.pop(missing_field)
    with pytest.raises(ValidationError):
        RegisteredNode(**data)

def test_registered_node_secrets_default_and_not_shared():
    n1 = RegisteredNode(**_valid_node_data())
    n2 = RegisteredNode(**_valid_node_data() | {"name": "another", "namespace": "ns2"})
    assert isinstance(n1.secrets, list)
    assert isinstance(n2.secrets, list)
    assert n1.secrets == []
    assert n2.secrets == []
    assert n1.secrets is not n2.secrets
    n1.secrets.append("S1")
    assert n1.secrets == ["S1"]
    assert n2.secrets == []  # ensure no shared mutable default

def test_registered_node_invalid_schema_types_raise():
    bad_inputs = _valid_node_data() | {"inputs_schema": "not-a-dict"}
    with pytest.raises(ValidationError):
        RegisteredNode(**bad_inputs)
    bad_outputs = _valid_node_data() | {"outputs_schema": ["also", "not", "a", "dict"]}
    with pytest.raises(ValidationError):
        RegisteredNode(**bad_outputs)

def test_settings_contains_unique_index_over_name_and_namespace():
    # Validate presence and structure of the compound unique index (name, namespace).
    settings = getattr(RegisteredNode, "Settings", None)
    assert settings is not None, "Settings class is missing on RegisteredNode"
    indexes = getattr(settings, "indexes", None)
    assert indexes, "No indexes defined on RegisteredNode.Settings"

    unique_doc = None
    for idx in indexes:
        # PyMongo's IndexModel exposes a .document property with details.
        doc = getattr(idx, "document", None)
        if not doc:
            continue
        if doc.get("name") == "unique_name_namespace":
            unique_doc = doc
            break

    assert unique_doc is not None, "Expected index 'unique_name_namespace' not found."
    assert unique_doc.get("unique") is True
    key = unique_doc.get("key")
    # key may be a SON/OrderedDict or list of pairs depending on PyMongo internals
    if hasattr(key, "items"):
        key_items = list(key.items())
    else:
        key_items = list(key)
    assert key_items == [("name", 1), ("namespace", 1)], f"Unexpected index key ordering/fields: {key_items}"

@pytest.mark.asyncio
async def test_get_by_name_and_namespace_happy_path(monkeypatch):
    expected = object()
    captured = {}
    async def fake_find_one(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return expected

    monkeypatch.setattr(RegisteredNode, "find_one", fake_find_one, raising=True)
    result = await RegisteredNode.get_by_name_and_namespace("node-1", "ns-1")
    assert result is expected
    assert tuple(captured.get("args", ())) and not captured.get("kwargs")
    # Ensure filters contain the provided values (string representation fallback for ODM expressions)
    args_str = " ".join(map(lambda a: f"{a!r}", captured["args"]))
    assert "node-1" in args_str
    assert "ns-1" in args_str

@pytest.mark.asyncio
async def test_get_by_name_and_namespace_not_found(monkeypatch):
    async def fake_find_one(*_args, **_kwargs):
        return None
    monkeypatch.setattr(RegisteredNode, "find_one", fake_find_one, raising=True)
    result = await RegisteredNode.get_by_name_and_namespace("missing", "ns")
    assert result is None

@pytest.mark.asyncio
async def test_list_nodes_by_templates_empty_short_circuits(monkeypatch):
    called = {"find": False}
    def fake_find(_query):
        called["find"] = True
        # Should not be called when templates list is empty
        class _C:
            async def to_list(self):
                return []
        return _C()
    monkeypatch.setattr(RegisteredNode, "find", fake_find, raising=True)
    result = await RegisteredNode.list_nodes_by_templates([])
    assert result == []
    assert called["find"] is False

@pytest.mark.asyncio
async def test_list_nodes_by_templates_builds_correct_query_and_returns_results(monkeypatch):
    t1 = _DummyTemplate("alpha", "ns-a")
    t2 = _DummyTemplate("beta", "ns-b")

    expected = [object(), object()]
    captured = {}

    class _Cursor:
        def __init__(self, items): self._items = items
        async def to_list(self): return self._items

    def fake_find(query):
        captured["query"] = query
        return _Cursor(expected)

    monkeypatch.setattr(RegisteredNode, "find", fake_find, raising=True)

    result = await RegisteredNode.list_nodes_by_templates([t1, t2])
    assert result == expected

    q = captured.get("query")
    assert isinstance(q, dict) and "$or" in q
    or_clause = q["$or"]
    assert isinstance(or_clause, list) and len(or_clause) == 2
    assert {"name": "alpha", "namespace": "ns-a"} in or_clause
    assert {"name": "beta", "namespace": "ns-b"} in or_clause