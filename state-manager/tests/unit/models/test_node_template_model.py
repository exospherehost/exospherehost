"""
Test suite for NodeTemplate and Unites models.

Testing library/framework: pytest (with Pydantic v2 ValidationError assertions).

Covers:
- Successful model creation with valid data
- Validators: node_name, identifier (non-empty), next_nodes (non-empty, unique)
- Optional field `next_nodes` can be None
- Optional nested model `unites` with identifier non-empty when provided
- get_dependent_strings: returns one entry per input; raises on non-string values; handles empty inputs
"""

import builtins
import types
import sys
import inspect
import pytest

try:
    # Try common import paths — adapt if project layout differs.
    # Prefer the actual model module housing NodeTemplate and Unites.
    from state_manager.models.node_template_model import NodeTemplate, Unites  # type: ignore
    import state_manager.models.node_template_model as node_template_module  # type: ignore
except Exception:
    try:
        from state_manager.models.node_template import NodeTemplate, Unites  # type: ignore
        import state_manager.models.node_template as node_template_module  # type: ignore
    except Exception:
        # Fallback: dynamically locate the module that defines NodeTemplate in sys.modules
        # This keeps tests resilient if the path changes while still validating behavior.
        candidates = []
        for name, mod in list(sys.modules.items()):
            if not isinstance(mod, types.ModuleType):
                continue
            try:
                if hasattr(mod, "NodeTemplate") and hasattr(mod, "Unites"):
                    candidates.append(mod)
            except Exception:
                continue
        if not candidates:
            # Attempt a lazy import scan by probing typical packages under repo
            # This is a last-resort guard — if it fails, tests will clearly indicate missing module.
            raise
        node_template_module = candidates[0]
        NodeTemplate = getattr(node_template_module, "NodeTemplate")
        Unites = getattr(node_template_module, "Unites")


from pydantic import ValidationError


def _valid_payload(**overrides):
    data = {
        "node_name": "node_A",
        "namespace": "ns.main",
        "identifier": "node-A-id",
        "inputs": {"foo": "bar", "alpha": "beta"},
        "next_nodes": ["node_B", "node_C"],
        "unites": Unites(identifier="u-1"),
    }
    data.update(overrides)
    return data


class TestNodeTemplateValidation:
    def test_valid_creation_happy_path(self):
        model = NodeTemplate(**_valid_payload())
        assert model.node_name == "node_A"
        assert model.namespace == "ns.main"
        assert model.identifier == "node-A-id"
        assert model.next_nodes == ["node_B", "node_C"]
        assert model.unites is not None and model.unites.identifier == "u-1"

    @pytest.mark.parametrize(
        "field, bad_value, expected_msg",
        [
            ("node_name", "", "Node name cannot be empty"),
            ("identifier", "", "Node identifier cannot be empty"),
        ],
    )
    def test_required_string_fields_must_not_be_empty(self, field, bad_value, expected_msg):
        payload = _valid_payload(**{field: bad_value})
        with pytest.raises(ValidationError) as ei:
            NodeTemplate(**payload)
        # ValueError raised in field_validator should surface inside ValidationError text
        assert expected_msg in str(ei.value)

    def test_next_nodes_none_is_allowed(self):
        payload = _valid_payload(next_nodes=None)
        model = NodeTemplate(**payload)
        assert model.next_nodes is None

    def test_next_nodes_rejects_empty_and_duplicates_with_aggregated_errors(self):
        # includes duplicate "dup" and an empty string
        payload = _valid_payload(next_nodes=["ok1", "dup", "dup", ""])
        with pytest.raises(ValidationError) as ei:
            NodeTemplate(**payload)
        msg = str(ei.value)
        assert "Next node identifier dup is not unique" in msg
        assert "Next node identifier cannot be empty" in msg

    def test_unites_identifier_must_not_be_empty_when_provided(self):
        payload = _valid_payload(unites=Unites(identifier=""))
        with pytest.raises(ValidationError) as ei:
            NodeTemplate(**payload)
        assert "Unites identifier cannot be empty" in str(ei.value)


class TestGetDependentStrings:
    def test_returns_one_dependent_string_per_input_value(self):
        payload = _valid_payload(inputs={"a": "X", "b": "Y", "c": "Z"})
        model = NodeTemplate(**payload)

        # Prefer not to mock: assert count and type if available
        result = model.get_dependent_strings()
        assert isinstance(result, list)
        assert len(result) == 3

        # If DependentString is importable from the module, verify type
        DepStr = getattr(node_template_module, "DependentString", None)
        if DepStr is not None and inspect.isclass(DepStr):
            assert all(isinstance(d, DepStr) for d in result)

    def test_raises_value_error_when_any_input_value_is_not_string(self):
        payload = _valid_payload(inputs={"a": "X", "b": 123, "c": "Z"})
        model = NodeTemplate(**payload)
        with pytest.raises(ValueError) as ei:
            model.get_dependent_strings()
        assert "Input 123 is not a string" in str(ei.value)

    def test_handles_empty_inputs_dict(self):
        payload = _valid_payload(inputs={})
        model = NodeTemplate(**payload)
        out = model.get_dependent_strings()
        assert out == []


# Extra edge cases: whitespace-only strings considered non-empty by type,
# but validators explicitly only check for equality with empty string.
# Decide expected behavior: whitespace is allowed per current implementation.
def test_whitespace_strings_are_allowed_by_validators():
    payload = _valid_payload(node_name="  name  ", identifier="  id  ")
    model = NodeTemplate(**payload)
    assert model.node_name.strip() == "name"
    assert model.identifier.strip() == "id"