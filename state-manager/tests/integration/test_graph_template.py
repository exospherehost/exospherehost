from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.node_template_model import NodeTemplate

async def test_graph_template(app_started):
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
