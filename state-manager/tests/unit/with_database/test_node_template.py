import pytest
from app.models.node_template_model import NodeTemplate, Unites

def test_invalid_node_template(app_started):
    """Test invalid node template"""
    with pytest.raises(ValueError) as exc_info:
        NodeTemplate(
            node_name="",
            namespace="test_namespace",
            identifier="node1",
            inputs={},
            next_nodes=None,
            unites=None
        )
    assert "Node name cannot be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="",
            inputs={},
            next_nodes=None,
            unites=None
        )
    assert "Node identifier cannot be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="node1",
            inputs={},
            next_nodes=["", "node2"],
            unites=None
        )
    assert "Next node identifier cannot be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="node1",
            inputs={},
            next_nodes=["node1", "node1"],
            unites=None
        )
    assert "Next node identifier node1 is not unique" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="node1",
            inputs={},
            next_nodes=["node2"],
            unites=Unites(identifier="")
        )
    assert "Unites identifier cannot be empty" in str(exc_info.value)

def test_get_dependent_strings(app_started):
    """Test get dependent strings"""
    node_template = NodeTemplate(
        node_name="test_node",
        namespace="test_namespace",
        identifier="node1",
        inputs={"input1": "${{node2.outputs.output1}}"},
        next_nodes=None,
        unites=None
    )
    dependent_strings = node_template.get_dependent_strings()
    assert len(dependent_strings) == 1
    assert dependent_strings[0].get_identifier_field() == [("node2", "output1")]

    node_template = NodeTemplate(
        node_name="test_node",
        namespace="test_namespace",
        identifier="node1",
        inputs={"input1": "${{node2.outputs.output1}}", "input2": "${{node3.outputs.output2}}"},
        next_nodes=None,
        unites=None
    )
    dependent_strings = node_template.get_dependent_strings()
    assert len(dependent_strings) == 2
    assert ("node2", "output1") in dependent_strings[0].get_identifier_field()
    assert ("node3", "output2") in dependent_strings[1].get_identifier_field()

    with pytest.raises(ValueError) as exc_info:
        node_template = NodeTemplate(
            node_name="test_node",
            namespace="test_namespace",
            identifier="node1",
            inputs={"input1": 1},
            next_nodes=None,
            unites=None
        )
        dependent_strings = node_template.get_dependent_strings()
    assert "Input 1 is not a string" in str(exc_info.value)