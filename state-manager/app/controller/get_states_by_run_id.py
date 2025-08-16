"""
Controller for fetching states by run ID
"""
from typing import List

from ..models.db.state import State
from ..singletons.logs_manager import LogsManager


async def get_states_by_run_id(namespace: str, run_id: str, request_id: str) -> List[State]:
    """
    Get all states for a given run ID in a namespace
    
    Args:
        namespace: The namespace to search in
        run_id: The run ID to filter by
        request_id: Request ID for logging
        
    Returns:
        List of states for the given run ID
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info(f"Fetching states for run ID: {run_id} in namespace: {namespace}", x_exosphere_request_id=request_id)
        
        # Find all states for the run ID in the namespace
        states = await State.find(
            State.run_id == run_id,
            State.namespace_name == namespace
        ).to_list()
        
        logger.info(f"Found {len(states)} states for run ID: {run_id}", x_exosphere_request_id=request_id)
        
        return states
        
    except Exception as e:
        logger.error(f"Error fetching states for run ID {run_id} in namespace {namespace}: {str(e)}", x_exosphere_request_id=request_id)
        raise
