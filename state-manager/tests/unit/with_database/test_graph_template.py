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
async def test_basic_invalid_graphs(app_started):
    """Test invalid graphs with empty name and namespace"""

    # test invalid graph with empty name and namespace
    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="",
            namespace="",
            nodes=[],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Name cannot be empty" in str(exc_info.value)
    assert "Namespace cannot be empty" in str(exc_info.value)

    # test invalid graph with non-unique node identifiers
    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_name",
            namespace="test_namespace",
            nodes=[
                NodeTemplate(
                    node_name="node1",
                    namespace="test_namespace",
                    identifier="node1",
                    inputs={},
                    next_nodes=None,
                    unites=None
                ),
                NodeTemplate(
                    node_name="node2",
                    namespace="test_namespace",
                    identifier="node1",
                    inputs={},
                    next_nodes=None,
                    unites=None
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Node identifier node1 is not unique" in str(exc_info.value)

    # test invalid graph with non-existing node identifiers
    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_name",
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
                    unites = None
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Node identifier node3 does not exist in the graph" in str(exc_info.value)

    # test invalid graph with non-existing unites identifiers
    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_name",
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
                    unites = Unites(
                        identifier="node3"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Node node2 has an unites target node3 that does not exist" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_name",
            namespace="test_namespace",
            nodes=[],
            validation_status=GraphTemplateValidationStatus.PENDING,
            secrets={
                "secret1": "",
            }
        )
    assert "Secrets cannot be empty" in str(exc_info.value)

    # test invalid graph with non-urlsafe base64 encoded secret
    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_name",
            namespace="test_namespace",
            nodes=[],
            validation_status=GraphTemplateValidationStatus.PENDING,
            secrets={
                "secret1": "invalid_base64_string_that_is_long_enough_to_pass_length_check_but_not_valid_base64_encoding_123456789",
            }
        )
    assert "Value is not valid URL-safe base64 encoded" in str(exc_info.value)

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
                    # flipped the order, both cases should work the same
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


@pytest.mark.asyncio
async def test_invalid_graphs_with_disconnected_nodes(app_started):
    """Test invalid graphs with disconnected nodes"""
    with pytest.raises(ValueError, match="Graph is disconnected"):
        GraphTemplate(
            name="test_liner_graph_template_1",
            namespace="test_namespace",
            nodes=[
                NodeTemplate(
                    node_name="node1",
                    namespace="test_namespace",
                    identifier="node1",
                    inputs={},
                    next_nodes=[
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
                        identifier="node4"
                    )
                ),
                NodeTemplate(
                    node_name="node4",
                    namespace="test_namespace",
                    identifier="node4",
                    inputs={},
                    next_nodes=None,
                    unites=Unites(
                        identifier="node3"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )

    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_liner_graph_template_1",
            namespace="test_namespace",
            nodes=[
                NodeTemplate(
                    node_name="node1",
                    namespace="test_namespace",
                    identifier="node1",
                    inputs={},
                    next_nodes=None,
                    unites=None
                ),
                NodeTemplate(
                    node_name="node2",
                    namespace="test_namespace",
                    identifier="node2",
                    inputs={},
                    next_nodes=None,
                    unites=Unites(
                        identifier="node1"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "is not connected to the root node" in str(exc_info.value)

@pytest.mark.asyncio
async def test_valid_graph_inputs(app_started):
    """Test valid graph inputs"""
    graph_template_model = GraphTemplate(
        name="test_graph",
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
                inputs={
                    "input1": "${{node1.outputs.output1}}",
                    "input2": "${{node1.outputs.output2}}"
                },
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING
    )
    dependent_strings = graph_template_model.get_node_by_identifier("node2").get_dependent_strings()
    assert len(dependent_strings) == 2

    input_set: set[tuple[str, str]] = set()

    for dependent_string in dependent_strings:
        for identifier, field in dependent_string.get_identifier_field():
            input_set.add((identifier, field))

    assert len(input_set) == 2
    assert input_set == {("node1", "output1"), ("node1", "output2")}


    graph_template_model = GraphTemplate(
        name="test_graph",
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
                inputs={
                    "input1": "testing",
                    "input2": "${{node1.outputs.output2}}"
                },
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING
    )
    dependent_strings = graph_template_model.get_node_by_identifier("node2").get_dependent_strings()
    assert len(dependent_strings) == 2

    input_set: set[tuple[str, str]] = set()

    for dependent_string in dependent_strings:
        for identifier, field in dependent_string.get_identifier_field():
            input_set.add((identifier, field))

    assert len(input_set) == 1
    assert input_set == {("node1", "output2")}


@pytest.mark.asyncio
async def test_invalid_graph_inputs(app_started):
    """Test invalid graph inputs"""
    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_graph",
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
                    inputs={
                        "input1": "${{node1.outputs.output1}}",
                        "input2": "${{node2.outputs.output2}}"
                    },
                    next_nodes=None,
                    unites=None
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Input ${{node2.outputs.output2}} depends on node2 but node2 is not a parent of node2" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_graph",
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
                    inputs={
                        "input1": "${{node2.outputs.output1}}"
                    },
                    next_nodes=None,
                    unites=Unites(
                        identifier="node1"
                    )
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Input ${{node2.outputs.output1}} depends on node2 but node2 is not a parent of node3" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_graph",
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
                    inputs={
                        "input1": 123
                    },
                    next_nodes=None,
                    unites=None
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "is not a string" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        GraphTemplate(
            name="test_graph",
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
                    inputs={
                        "input1": "${{node1.outputs.output1"
                    },
                    next_nodes=None,
                    unites=None
                )
            ],
            validation_status=GraphTemplateValidationStatus.PENDING
        )
    assert "Error creating dependent string for input ${{node1.outputs.output1" in str(exc_info.value)