import pytest
from unittest.mock import AsyncMock, patch

from pydantic import BaseModel

from app.tasks import create_next_states as cns
from app.models.node_template_model import NodeTemplate, Unites
from app.models.state_status_enum import StateStatusEnum


# ---------------------------------------------------------------------------
# Helper fixtures & stubs
# ---------------------------------------------------------------------------

class DummyState:
    """Very small stand-in for the real *State* ODM model.

    Only the minimal surface required by the functions under test is
    implemented (``status``, ``outputs`` and an async ``save`` method).
    """

    def __init__(self, sid, outputs=None):
        self.id = sid
        self.status = None
        self.outputs = outputs or {}
        self.error = None
        # ``save`` must be awaitable because the real method is awaited.
        self.save = AsyncMock()


class DummyQuery:
    """Mimics the chain returned by ``State.find()`` inside the helpers."""

    def __init__(self, count_value: int = 0):
        self._count_value = count_value
        self.set = AsyncMock()

    async def count(self):
        return self._count_value


# ---------------------------------------------------------------------------
# Tests for *get_dependents*
# ---------------------------------------------------------------------------

def test_get_dependents_success():
    src = "Hello ${{parent1.outputs.field1}} world ${{current.outputs.answer}}!"
    result = cns.get_dependents(src)

    # Head extraction
    assert result.head == "Hello "

    # Two placeholders discovered in order
    assert list(result.dependents.keys()) == [0, 1]

    d0 = result.dependents[0]
    assert (d0.identifier, d0.field, d0.tail) == ("parent1", "field1", " world ")

    d1 = result.dependents[1]
    assert (d1.identifier, d1.field, d1.tail) == ("current", "answer", "!")


def test_get_dependents_invalid_format():
    # Missing the mandatory ``.outputs.`` part should error out.
    with pytest.raises(ValueError):
        cns.get_dependents("Broken ${{parent.outputs_missing}} snippet")


# ---------------------------------------------------------------------------
# Tests for *validate_dependencies*
# ---------------------------------------------------------------------------

class _InputModel(BaseModel):
    greeting: str


@pytest.fixture
def parent_state():
    return DummyState("parent-sid", outputs={"msg": "hi"})


def _make_node_template(dep_string: str) -> NodeTemplate:
    return NodeTemplate(
        node_name="next_node",
        namespace="ns",
        identifier="next_id",
        inputs={"greeting": dep_string},
        next_nodes=[],
        unites=None,
    )


def test_validate_dependencies_success(parent_state):
    node_tpl = _make_node_template("${{parent.outputs.msg}}")
    # Should not raise.
    cns.validate_dependencies(node_tpl, _InputModel, "current", {"parent": parent_state})


def test_validate_dependencies_missing_parent(parent_state):
    node_tpl = _make_node_template("${{missing_parent.outputs.msg}}")
    with pytest.raises(KeyError):
        cns.validate_dependencies(node_tpl, _InputModel, "current", {"parent": parent_state})


# ---------------------------------------------------------------------------
# Tests for *check_unites_satisfied*
# ---------------------------------------------------------------------------

async def _run_check_unites(count_value):
    unit = Unites(identifier="parent")
    node_tpl = NodeTemplate(
        node_name="node",
        namespace="ns",
        identifier="id",
        inputs={},
        next_nodes=[],
        unites=[unit],
    )

    # Patch *State.find()* to deliver the dummy query with desired count.
    with patch.object(cns, "State") as mock_state:
        mock_state.find.return_value = DummyQuery(count_value)
        result = await cns.check_unites_satisfied(
            "ns", "graph", node_tpl, {"parent": "parent-sid"} # type: ignore
        )
    return result


@pytest.mark.asyncio
async def test_check_unites_satisfied_true():
    assert await _run_check_unites(0) is True


@pytest.mark.asyncio
async def test_check_unites_satisfied_false():
    assert await _run_check_unites(1) is False


# ---------------------------------------------------------------------------
# Tests for *mark_success_states*
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mark_success_states_updates_status():
    state_ids = ["sid-1", "sid-2"]
    created = {}

    async def _get(sid):
        created[sid] = DummyState(sid)
        return created[sid]

    with patch.object(cns, "State") as mock_state:
        # Provide *get* and *find* replacements.
        mock_state.get = AsyncMock(side_effect=_get)
        mock_state.find.return_value = DummyQuery()

        # Execute.
        await cns.mark_success_states(state_ids) # type: ignore

    for st in created.values():
        assert st.status == StateStatusEnum.SUCCESS
        st.save.assert_awaited()