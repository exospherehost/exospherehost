"""
Controller for listing distinct namespaces from registered nodes
"""
from typing import List

from ..models.db.registered_node import RegisteredNode
from ..singletons.logs_manager import LogsManager


async def list_namespaces(request_id: str) -> List[str]:
    """
    List all distinct namespaces from registered nodes
    
    Args:
        request_id: Request ID for logging
        
    Returns:
        List of distinct namespace strings
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info("Listing distinct namespaces from registered nodes", x_exosphere_request_id=request_id)
        
        # Use MongoDB aggregation to get distinct namespaces
        pipeline = [
            {"$group": {"_id": "$namespace"}},
            {"$sort": {"_id": 1}}
        ]
        
        result = await RegisteredNode.aggregate(pipeline).to_list()
        namespaces = [doc["_id"] for doc in result if doc["_id"]]
        
        logger.info(f"Found {len(namespaces)} distinct namespaces", x_exosphere_request_id=request_id)
        
        return namespaces
        
    except Exception as e:
        logger.error(f"Error listing namespaces: {str(e)}", x_exosphere_request_id=request_id)
        raise 