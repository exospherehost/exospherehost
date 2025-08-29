import pytest

from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.node_template_model import NodeTemplate

@pytest.mark.asyncio
async def test_graph_template_basic(app_started):
    """Test graph template creation"""
    graph_template_model = GraphTemplate(
        name="test_graph_template",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="test_node_template",
                namespace="test_namespace",
                identifier="test_identifier",
                inputs={},
                next_nodes=[],
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING,
    )
    assert graph_template_model.name == "test_graph_template"

@pytest.mark.asyncio
async def test_liner_graph_template(app_started):
    """Test liner graph template creation"""
    graph_template_model = GraphTemplate(
        name="test_liner_graph_template",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="node1",
                namespace="test_namespace",
                identifier="node1",
                inputs={},
                next_nodes=[
                    "node2"
                ],
                unites=None
            ),
            NodeTemplate(
                node_name="node2",
                namespace="test_namespace",
                identifier="node2",
                inputs={},
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING
    )
    assert graph_template_model.get_root_node().identifier == "node1"
    assert graph_template_model.get_parents_by_identifier("node1") == set()
    assert graph_template_model.get_parents_by_identifier("node2") == {"node1"}
    assert graph_template_model.get_node_by_identifier("node1").identifier == "node1" # type: ignore
    assert graph_template_model.get_node_by_identifier("node2").identifier == "node2" # type: ignore


@pytest.mark.asyncio
async def test_graph_template_invalid_liner_graph_template(app_started):
    """Test invalid liner graph template creation"""
    with pytest.raises(ValueError, match="There should be exactly one root node in the graph but found 0 nodes with zero in-degree: \\[\\]"):
        GraphTemplate(
            name="test_invalid_liner_graph_template",
            namespace="test_namespace",
            nodes=[],
            validation_status=GraphTemplateValidationStatus.PENDING
        )