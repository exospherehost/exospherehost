from app.models.db.graph_template_model import GraphTemplate, NodeTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.registered_node import RegisteredNode
from app.singletons.logs_manager import LogsManager
from beanie.operators import In
from json_schema_to_pydantic import create_model

logger = LogsManager().get_logger()

async def verify_nodes_names(nodes: list[NodeTemplate], errors: list[str]):
    for node in nodes:
        if node.node_name is None or node.node_name == "":
            errors.append(f"Node {node.identifier} has no name")

async def verify_nodes_namespace(nodes: list[NodeTemplate], graph_namespace: str, errors: list[str]):
    for node in nodes:
        if node.namespace != graph_namespace and node.namespace != "exospherehost":
            errors.append(f"Node {node.identifier} has invalid namespace '{node.namespace}'. Must match graph namespace '{graph_namespace}' or use universal namespace 'exospherehost'")

async def verify_node_exists(nodes: list[NodeTemplate], database_nodes: list[RegisteredNode], errors: list[str]):
    template_nodes_set = set([(node.node_name, node.namespace) for node in nodes])
    database_nodes_set = set([(node.name, node.namespace) for node in database_nodes])

    nodes_not_found = template_nodes_set - database_nodes_set
    
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

async def verify_secrets(graph_template: GraphTemplate, database_nodes: list[RegisteredNode], errors: list[str]):
    required_secrets_set = set()

    for node in database_nodes:
        if node.secrets is None:
            continue
        for secret in node.secrets:
            required_secrets_set.add(secret)
    
    present_secrets_set = set()
    for secret_name in graph_template.secrets.keys():
        present_secrets_set.add(secret_name)
    
    missing_secrets_set = required_secrets_set - present_secrets_set
    
    for secret_name in missing_secrets_set:
        errors.append(f"Secret {secret_name} is required but not present in the graph template")
 

async def get_database_nodes(nodes: list[NodeTemplate], graph_namespace: str):
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
    return graph_namespace_database_nodes + exospherehost_database_nodes


async def verify_inputs(graph_nodes: list[NodeTemplate], database_nodes: list[RegisteredNode], dependency_graph: dict[str, list[str]], errors: list[str]):
    look_up_table = {}
    for node in graph_nodes:
        look_up_table[node.identifier] = {"graph_node": node}

        for database_node in database_nodes:
            if database_node.name == node.node_name and database_node.namespace == node.namespace:
                look_up_table[node.identifier]["database_node"] = database_node
                break

    for node in graph_nodes:
        try:
            model_class = create_model(look_up_table[node.identifier]["database_node"].inputs_schema)

            for field_name, field_info in model_class.model_fields.items():
                if field_info.annotation is not str:
                    errors.append(f"{node.node_name}.Inputs field '{field_name}' must be of type str, got {field_info.annotation}")
                    continue

                if field_name not in look_up_table[node.identifier]["graph_node"].inputs.keys():
                    errors.append(f"{node.node_name}.Inputs field '{field_name}' not found in graph template")
                    continue

                # get ${{ identifier.outputs.field_name }} objects from the string
                splits = look_up_table[node.identifier]["graph_node"].inputs[field_name].split("${{")
                for split in splits[1:]:
                    if "}}" in split:

                        identifier = None
                        field = None

                        syntax_string = split.split("}}")[0].strip()

                        parts = syntax_string.split(".")
                        if len(parts) == 3 and parts[1].strip() == "outputs":
                            identifier, field = parts[0].strip(), parts[2].strip()
                        else:
                            errors.append(f"{node.node_name}.Inputs field '{field_name}' references field {syntax_string} which is not a valid output field")
                            continue
                        
                        if identifier is None or field is None:
                            errors.append(f"{node.node_name}.Inputs field '{field_name}' references field {syntax_string} which is not a valid output field")
                            continue

                        if identifier not in dependency_graph[node.identifier]:
                            errors.append(f"{node.node_name}.Inputs field '{field_name}' references node {identifier} which is not a dependency of {node.identifier}")
                            continue
                        
                        output_model_class = create_model(look_up_table[identifier]["database_node"].outputs_schema)
                        if field not in output_model_class.model_fields.keys():
                            errors.append(f"{node.node_name}.Inputs field '{field_name}' references field {field} of node {identifier} which is not a valid output field")
                            continue
                
        except Exception as e:
            errors.append(f"Error creating input model for node {node.identifier}: {str(e)}")

async def build_dependencies_graph(graph_nodes: list[NodeTemplate]):
    dependency_graph = {}
    for node in graph_nodes:
        dependency_graph[node.identifier] = set()
        if node.next_nodes is None:
            continue
        for next_node in node.next_nodes:
            dependency_graph[next_node].add(node.identifier)
            dependency_graph[next_node] = dependency_graph[next_node] | dependency_graph[node.identifier]
    return dependency_graph

async def verify_topology(graph_nodes: list[NodeTemplate], errors: list[str]):
    # verify that the graph is a tree
    # verify that the graph is connected
    dependencies = {}
    identifier_to_node = {}
    visited = {}
    dependency_graph = {}

    for node in graph_nodes:
        if node.identifier in dependencies.keys():
            errors.append(f"Multiple identifier {node.identifier} incorrect topology")
            return
        dependencies[node.identifier] = set()
        identifier_to_node[node.identifier] = node
        visited[node.identifier] = False
    
    # verify that there exists only one root node
    for node in graph_nodes:
        if node.next_nodes is None:
            continue
        for next_node in node.next_nodes:
            dependencies[next_node].add(node.identifier)

    # verify that there exists only one root node
    root_nodes = [node for node in graph_nodes if len(dependencies[node.identifier]) == 0]
    if len(root_nodes) != 1:
        errors.append(f"Graph has {len(root_nodes)} root nodes, expected 1")
        return
    
    
    # verify that the graph is a tree using recursive DFS and store the dependency graph
    def dfs_visit(current_node: str, parent_node: str | None = None, current_path: list[str] = []):

        if visited[current_node]:
            if parent_node is not None:
                errors.append(f"Graph is not a tree at {parent_node} -> {current_node}")
            return
        
        visited[current_node] = True
        dependency_graph[current_node] = current_path.copy()       

        if identifier_to_node[current_node].next_nodes is None:
            return
        
        current_path.append(current_node)
            
        for next_node in identifier_to_node[current_node].next_nodes:
            dfs_visit(next_node, current_node, current_path)

        current_path.pop()        
    
    # Start DFS from root node
    dfs_visit(root_nodes[0].identifier)
    
    # Check connectivity
    for identifier, visited_value in visited.items():
        if not visited_value:
            errors.append(f"Graph is not connected at {identifier}")
    
    return dependency_graph

async def verify_unites(graph_nodes: list[NodeTemplate], dependency_graph: dict | None, errors: list[str]):
    if dependency_graph is None:
        return
    
    for node in graph_nodes:
        if node.unites is None or len(node.unites) == 0:
            continue
        for depend in node.unites:
            if depend.identifier not in dependency_graph[node.identifier]:
                errors.append(f"Node {node.identifier} depends on {depend.identifier} which is not a dependency of {node.identifier}")
    

async def verify_graph(graph_template: GraphTemplate):
    try:
        errors = []
        database_nodes = await get_database_nodes(graph_template.nodes, graph_template.namespace)

        await verify_nodes_names(graph_template.nodes, errors)
        await verify_nodes_namespace(graph_template.nodes, graph_template.namespace, errors)
        await verify_node_exists(graph_template.nodes, database_nodes, errors)
        await verify_node_identifiers(graph_template.nodes, errors)
        await verify_secrets(graph_template, database_nodes, errors)
        dependency_graph = await verify_topology(graph_template.nodes, errors)

        if dependency_graph is not None and len(errors) == 0:        
            await verify_inputs(graph_template.nodes, database_nodes, dependency_graph, errors)

        await verify_unites(graph_template.nodes, dependency_graph, errors)

        if errors or dependency_graph is None:
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