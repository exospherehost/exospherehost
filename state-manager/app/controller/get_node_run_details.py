"""
Controller for getting detailed information about a specific node in a run
"""
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from ..models.db.state import State
from ..models.node_run_details_models import NodeRunDetailsResponse
from ..singletons.logs_manager import LogsManager


async def get_node_run_details(namespace: str, graph_name: str, run_id: str, node_id: str, request_id: str) -> NodeRunDetailsResponse:
    """
    Get detailed information about a specific node in a run
    
    Args:
        namespace: The namespace to search in
        graph_name: The graph name to filter by
        run_id: The run ID to filter by
        node_id: The node ID (state ID) to get details for
        request_id: Request ID for logging
        
    Returns:
        NodeRunDetailsResponse containing detailed node information
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info(f"Getting node run details for node ID: {node_id} in run: {run_id}, graph: {graph_name}, namespace: {namespace}", x_exosphere_request_id=request_id)
        
        # Convert node_id to ObjectId if it's a valid ObjectId string
        try:
            node_object_id = PydanticObjectId(node_id)
        except Exception:
            logger.error(f"Invalid node ID format: {node_id}", x_exosphere_request_id=request_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid node ID format: {node_id}"
            )
        
        # Find the specific state
        state = await State.find_one(
            State.id == node_object_id,
            State.run_id == run_id,
            State.graph_name == graph_name,
            State.namespace_name == namespace
        )
        
        if not state:
            logger.warning(f"Node not found: {node_id} in run: {run_id}, graph: {graph_name}, namespace: {namespace}", x_exosphere_request_id=request_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node {node_id} not found in run {run_id} for graph {graph_name}"
            )
        
        # Convert parent ObjectIds to strings
        parent_identifiers = {}
        for identifier, parent_id in state.parents.items():
            parent_identifiers[identifier] = str(parent_id)
        
        # Create response
        response = NodeRunDetailsResponse(
            id=str(state.id),
            node_name=state.node_name,
            identifier=state.identifier,
            graph_name=state.graph_name,
            run_id=state.run_id,
            status=state.status,
            inputs=state.inputs,
            outputs=state.outputs,
            error=state.error,
            parents=parent_identifiers,
            created_at=state.created_at.isoformat() if state.created_at else "",
            updated_at=state.updated_at.isoformat() if state.updated_at else ""
        )
        
        logger.info(f"Successfully retrieved node run details for node ID: {node_id}", x_exosphere_request_id=request_id)
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting node run details for node ID: {node_id}: {str(e)}", x_exosphere_request_id=request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while retrieving node details"
        ) 