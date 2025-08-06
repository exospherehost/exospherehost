from app.models.db.graph_template_model import GraphTemplate, NodeTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.registered_node import RegisteredNode
from app.singletons.logs_manager import LogsManager
from beanie.operators import In

logger = LogsManager().get_logger()

async def verify_nodes_names(nodes: list[NodeTemplate], errors: list[str]):
    for node in nodes:
        if node.node_name is None or node.node_name == "":
            errors.append(f"Node {node.identifier} has no name")

async def verify_nodes_namespace(nodes: list[NodeTemplate], graph_namespace: str, errors: list[str]):
    for node in nodes:
        if node.namespace != graph_namespace and node.namespace != "exospherehost":
            errors.append(f"Node {node.identifier} has invalid namespace '{node.namespace}'. Must match graph namespace '{graph_namespace}' or use universal namespace 'exospherehost'")

async def verify_node_exists(nodes: list[NodeTemplate], graph_namespace: str, errors: list[str]):
    graph_namespace_node_names = [
        node.node_name for node in nodes if node.namespace == graph_namespace
    ]
    graph_namespace_database_nodes = await RegisteredNode.find(
        In(RegisteredNode.name, graph_namespace_node_names),
        RegisteredNode.namespace == graph_namespace
    ).to_list()
    exospherehost_node_names = [
        node.node_name for node in nodes if node.namespace == "exospherehost"
    ]
    exospherehost_database_nodes = await RegisteredNode.find(
        In(RegisteredNode.name, exospherehost_node_names),
        RegisteredNode.namespace == "exospherehost"
    ).to_list()
    
    template_nodes = set([(node.node_name, node.namespace) for node in nodes])
    database_nodes = set([(node.name, node.namespace) for node in graph_namespace_database_nodes + exospherehost_database_nodes])

    nodes_not_found = template_nodes - database_nodes
    
    for node in nodes_not_found:
        errors.append(f"Node {node[0]} in namespace {node[1]} does not exist.")

async def verify_node_identifiers(nodes: list[NodeTemplate], errors: list[str]):
    identifier_to_nodes = {}

    # First pass: collect all nodes by identifier
    for node in nodes:
        if node.identifier is None or node.identifier == "":
            errors.append(f"Node {node.node_name} in namespace {node.namespace} has no identifier")
            continue
        
        if node.identifier not in identifier_to_nodes:
            identifier_to_nodes[node.identifier] = []
        identifier_to_nodes[node.identifier].append(node)

    # Check for duplicates and report all nodes sharing the same identifier
    for identifier, nodes_with_identifier in identifier_to_nodes.items():
        if len(nodes_with_identifier) > 1:
            node_list = ", ".join([f"{node.node_name} in namespace {node.namespace}" for node in nodes_with_identifier])
            errors.append(f"Duplicate identifier '{identifier}' found in nodes: {node_list}")

    # Check next_nodes references using the valid identifiers
    valid_identifiers = set(identifier_to_nodes.keys())
    for node in nodes:
        if node.next_nodes is None:
            continue
        for next_node in node.next_nodes:
            if next_node not in valid_identifiers:
                errors.append(f"Node {node.node_name} in namespace {node.namespace} has a next node {next_node} that does not exist in the graph")

async def verify_graph(graph_template: GraphTemplate):
    try:
        errors = []
        await verify_nodes_names(graph_template.nodes, errors)
        await verify_nodes_namespace(graph_template.nodes, graph_template.namespace, errors)
        await verify_node_exists(graph_template.nodes, graph_template.namespace, errors)
        await verify_node_identifiers(graph_template.nodes, errors)

        if errors:
            graph_template.validation_status = GraphTemplateValidationStatus.INVALID
            graph_template.validation_errors = errors
            await graph_template.save()
            return
        
        graph_template.validation_status = GraphTemplateValidationStatus.VALID
        graph_template.validation_errors = None
        await graph_template.save()
        
    except Exception as e:
        logger.error(f"Exception during graph validation for graph template {graph_template.id}: {str(e)}", exc_info=True)
        graph_template.validation_status = GraphTemplateValidationStatus.INVALID
        graph_template.validation_errors = [f"Validation failed due to unexpected error: {str(e)}"]
        await graph_template.save()