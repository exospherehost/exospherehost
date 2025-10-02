"""
Controller for building graph structure from states by run ID
"""
from typing import List, Dict

from ..models.db.state import State
from ..models.graph_structure_models import GraphStructureResponse, GraphNode, GraphEdge
from ..models.state_status_enum import StateStatusEnum
from ..singletons.logs_manager import LogsManager


async def get_graph_structure(namespace: str, run_id: str, request_id: str) -> GraphStructureResponse:
    """
    Build a graph structure from states for a given run ID
    
    Args:
        namespace: The namespace to search in
        run_id: The run ID to filter by
        request_id: Request ID for logging
        
    Returns:
        GraphStructureResponse containing nodes and edges
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info(f"Building graph structure for run ID: {run_id} in namespace: {namespace}", x_exosphere_request_id=request_id)
        
        # Find all states for the run ID in the namespace
        states = await State.find(
            State.run_id == run_id,
            State.namespace_name == namespace
        ).to_list()
        
        if not states:
            logger.warning(f"No states found for run ID: {run_id}", x_exosphere_request_id=request_id)
            return GraphStructureResponse(
                graph_name="",
                root_states=[],
                nodes=[],
                edges=[],
                node_count=0,
                edge_count=0,
                execution_summary={status.value: 0 for status in StateStatusEnum}
            )
        
        # Get graph name from first state (all states in a run should have same graph name)
        graph_name = states[0].graph_name
        
        # Create nodes from states
        nodes: List[GraphNode] = []
        state_id_to_node: Dict[str, GraphNode] = {}
        
        for state in states:
            node = GraphNode(
                id=str(state.id),
                node_name=state.node_name,
                identifier=state.identifier,
                status=state.status,
                error=state.error
            )
            nodes.append(node)
            state_id_to_node[str(state.id)] = node
        
        # Create edges from parent relationships
        edges: List[GraphEdge] = []
        edge_id_counter = 0

        root_states = []
        
        for state in states:
            state_id = str(state.id)
            
            # Process parent relationships - only create edges for direct parents
            # Since parents are accumulated, we only want the direct parent (not all ancestors)

            if len(state.parents) == 0:
                root_states.append(state_id_to_node[str(state.id)])
                continue        

            if state.parents:
                # Get the most recent parent (the one that was added last)
                # In Python 3.7+, dict.items() preserves insertion order
                # The most recent parent should be the last one added
                parent_items = list(state.parents.items())
                if parent_items:                    
                    _ , parent_id = parent_items[-1]                                   

                    parent_id_str = str(parent_id)
                    
                    # Check if parent exists in our nodes (should be in same run)
                    if parent_id_str in state_id_to_node:
                        edge = GraphEdge(
                            source=parent_id_str,
                            target=state_id,
                        )
                        edges.append(edge)
                        edge_id_counter += 1
        
        # Build execution summary - initialize all possible states with zero counts
        execution_summary: Dict[str, int] = {status.value: 0 for status in StateStatusEnum}
        for state in states:
            status = state.status.value
            execution_summary[status] += 1
        
        logger.info(f"Built graph structure with {len(nodes)} nodes and {len(edges)} edges for run ID: {run_id}", x_exosphere_request_id=request_id)
        
        return GraphStructureResponse(
            root_states=root_states,
            graph_name=graph_name,
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges),
            execution_summary=execution_summary
        )
        
    except Exception as e:
        logger.error(f"Error building graph structure for run ID {run_id} in namespace {namespace}: {str(e)}", x_exosphere_request_id=request_id)
        raise
