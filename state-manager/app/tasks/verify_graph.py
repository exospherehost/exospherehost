from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.graph_template_model import NodeTemplate
from app.models.db.registered_node import RegisteredNode
from beanie.operators import In

async def verify_nodes_names(nodes: list[NodeTemplate], errors: list[str]):
    for node in nodes:
        if node.node_name is None or node.node_name == "":
            errors.append(f"Node {node.identifier} has no name")

async def verify_nodes_namespace(nodes: list[NodeTemplate], graph_namespace: str, errors: list[str]):
    for node in nodes:
        if node.namespace != graph_namespace and node.namespace != "exospherehost":
            errors.append(f"Node {node.identifier} has a namespace that does not match the graph namespace or uses exospherehost universal namespace")

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
    identities = set()

    for node in nodes:
        if node.identifier is None or node.identifier == "":
            errors.append(f"Node {node.node_name} in namespace {node.namespace} has no identifier")
            continue
        if node.identifier in identities:
            errors.append(f"Node {node.node_name} has a duplicate identifier {node.identifier} in namespace {node.namespace}")
            continue
        else:
            identities.add(node.identifier)

    for node in nodes:
        if node.next_nodes is None:
            continue
        for next_node in node.next_nodes:
            if next_node not in identities:
                errors.append(f"Node {node.node_name} in namespace {node.namespace} has a next node {next_node} that does not exist in the graph")

async def verify_graph(graph_template: GraphTemplate):
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