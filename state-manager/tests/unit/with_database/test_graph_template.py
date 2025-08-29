from pydantic import NonNegativeInt
import pytest

from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.node_template_model import NodeTemplate, Unites

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
                next_nodes=[
                    "node3"
                ],
                unites=None
            ),
            NodeTemplate(
                node_name="node3",
                namespace="test_namespace",
                identifier="node3",
                inputs={},
                next_nodes=None,
                unites=Unites(
                    identifier="node1"
                )
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

    with pytest.raises(ValueError, match="There should be exactly one root node in the graph but found 0 nodes with zero in-degree: \\[\\]"):
        GraphTemplate(
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
                    unites=Unites(
                        identifier="node2"
                    )
                ),
                NodeTemplate(
                    node_name="node2",
                    namespace="test_namespace",
                    identifier="node2",
                    inputs={},
                    next_nodes=[
                        "node3"
                    ],
                    unites=None
                ),
                NodeTemplate(
                    node_name="node3",
                    namespace="test_namespace",
                    identifier="node3",
                    inputs={},
                    next_nodes=None,
                    unites=Unites(
                        identifier="node1"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )


@pytest.mark.asyncio
async def test_self_unites_validation(app_started):
    """Test self unites validation"""
    with pytest.raises(ValueError, match="Node node1 has an unites target node1 that is the same as the node itself"):
        GraphTemplate(
            name="test_invalid_liner_graph_template",
            namespace="test_namespace",
            nodes=[
                NodeTemplate(
                    node_name="node1",
                    namespace="test_namespace",
                    identifier="node1",
                    inputs={},
                    next_nodes=None,
                    unites=Unites(
                        identifier="node1"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )

@pytest.mark.asyncio
async def test_parents_propagation(app_started):
    """Test parents propagation"""
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
                next_nodes=[
                    "node3"
                ],
                unites=None
            ),
            NodeTemplate(
                node_name="node3",
                namespace="test_namespace",
                identifier="node3",
                inputs={},
                next_nodes=None,
                unites=Unites(
                    identifier="node1"
                )
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING
    )
    assert graph_template_model.get_root_node().identifier == "node1"
    assert graph_template_model.get_parents_by_identifier("node1") == set()
    assert graph_template_model.get_parents_by_identifier("node2") == {"node1"}
    assert graph_template_model.get_parents_by_identifier("node3") == {"node1"}


@pytest.mark.asyncio
async def test_invalid_graphs_with_cycles_without_unites(app_started):
    """Test invalid graphs with cycles without unites"""
    with pytest.raises(ValueError, match="Node node2 is not acyclic"):
        GraphTemplate(
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
                    next_nodes=[
                        "node3"
                    ],
                    unites=None
                ),
                NodeTemplate(
                    node_name="node3",
                    namespace="test_namespace",
                    identifier="node3",
                    inputs={},
                    next_nodes=[
                        "node2"
                    ],
                    unites=None
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )

@pytest.mark.asyncio
async def test_invalid_graphs_with_cycles_with_unites(app_started):
    """Test invalid graphs with cycles with unites"""
    with pytest.raises(ValueError, match="Node node2 is not acyclic"):
        GraphTemplate(
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
                    next_nodes=[
                        "node3"
                    ],
                    unites=None
                ),
                NodeTemplate(
                    node_name="node3",
                    namespace="test_namespace",
                    identifier="node3",
                    inputs={},
                    next_nodes=[
                        "node2"
                    ],
                    unites=Unites(
                        identifier="node1"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )


@pytest.mark.asyncio
async def test_valid_graphs_with_unites(app_started):
    """Test valid graphs with unites"""
    graph_template_model_1 = GraphTemplate(
        name="test_liner_graph_template_1",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="node1",
                namespace="test_namespace",
                identifier="node1",
                inputs={},
                next_nodes=[
                    "node2", 
                    "node3"
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
            ),
            NodeTemplate(
                node_name="node3",
                namespace="test_namespace",
                identifier="node3",
                inputs={},
                next_nodes=None,
                unites=Unites(
                    identifier="node2"
                )
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING
    )
    assert graph_template_model_1.get_root_node().identifier == "node1"
    assert graph_template_model_1.get_parents_by_identifier("node1") == set()
    assert graph_template_model_1.get_parents_by_identifier("node2") == {"node1"}
    assert graph_template_model_1.get_parents_by_identifier("node3") == {"node2", "node1"}
    assert graph_template_model_1.get_path_by_identifier("node1") == set()
    assert graph_template_model_1.get_path_by_identifier("node2") == {"node1"}
    assert graph_template_model_1.get_path_by_identifier("node3") == {"node1"}

    graph_template_model_2 = GraphTemplate(
        name="test_liner_graph_template_1",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="node1",
                namespace="test_namespace",
                identifier="node1",
                inputs={},
                next_nodes=[
                    # fliped the order, both cases should work the same
                    "node3", 
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
            ),
            NodeTemplate(
                node_name="node3",
                namespace="test_namespace",
                identifier="node3",
                inputs={},
                next_nodes=None,
                unites=Unites(
                    identifier="node2"
                )
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING
    )
    assert graph_template_model_2.get_root_node().identifier == "node1"
    assert graph_template_model_2.get_parents_by_identifier("node1") == set()
    assert graph_template_model_2.get_parents_by_identifier("node2") == {"node1"}
    assert graph_template_model_2.get_parents_by_identifier("node3") == {"node2", "node1"}
    assert graph_template_model_2.get_path_by_identifier("node1") == set()
    assert graph_template_model_2.get_path_by_identifier("node2") == {"node1"}
    assert graph_template_model_2.get_path_by_identifier("node3") == {"node1"}