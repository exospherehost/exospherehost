"""
Controller for listing registered nodes by namespace
"""
from typing import List

from ..models.db.registered_node import RegisteredNode
from ..singletons.logs_manager import LogsManager


async def list_registered_nodes(namespace: str, request_id: str) -> List[RegisteredNode]:
    """
    List all registered nodes for a given namespace
    
    Args:
        namespace: The namespace to list nodes for
        request_id: Request ID for logging
        
    Returns:
        List of registered nodes
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info(f"Listing registered nodes for namespace: {namespace}", x_exosphere_request_id=request_id)
        
        # Find all registered nodes for the namespace
        nodes = await RegisteredNode.find(
            RegisteredNode.namespace == namespace
        ).to_list()
        
        logger.info(f"Found {len(nodes)} registered nodes for namespace: {namespace}", x_exosphere_request_id=request_id)
        
        return nodes
        
    except Exception as e:
        logger.error(f"Error listing registered nodes for namespace {namespace}: {str(e)}", x_exosphere_request_id=request_id)
        raise
