"""
Controller for fetching current states in a namespace
"""
from typing import List

from ..models.db.state import State
from ..singletons.logs_manager import LogsManager


async def get_current_states(namespace: str, request_id: str) -> List[State]:
    """
    Get all current states in a namespace
    
    Args:
        namespace: The namespace to search in
        request_id: Request ID for logging
        
    Returns:
        List of all states in the namespace
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info(f"Fetching current states for namespace: {namespace}", x_exosphere_request_id=request_id)
        
        # Find all states in the namespace
        states = await State.find(
            State.namespace_name == namespace
        ).to_list()
        
        logger.info(f"Found {len(states)} states for namespace: {namespace}", x_exosphere_request_id=request_id)
        
        return states
        
    except Exception as e:
        logger.error(f"Error fetching current states for namespace {namespace}: {str(e)}", x_exosphere_request_id=request_id)
        raise
