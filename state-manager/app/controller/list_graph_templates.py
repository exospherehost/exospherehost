"""
Controller for listing graph templates by namespace
"""
from typing import List

from ..models.db.graph_template_model import GraphTemplate
from ..singletons.logs_manager import LogsManager


async def list_graph_templates(namespace: str, request_id: str) -> List[GraphTemplate]:
    """
    List all graph templates for a given namespace
    
    Args:
        namespace: The namespace to list graph templates for
        request_id: Request ID for logging
        
    Returns:
        List of graph templates
    """
    logger = LogsManager().get_logger()
    
    try:
        logger.info(f"Listing graph templates for namespace: {namespace}", x_exosphere_request_id=request_id)
        
        # Find all graph templates for the namespace
        templates = await GraphTemplate.find(
            GraphTemplate.namespace == namespace
        ).to_list()
        
        logger.info(f"Found {len(templates)} graph templates for namespace: {namespace}", x_exosphere_request_id=request_id)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error listing graph templates for namespace {namespace}: {str(e)}", x_exosphere_request_id=request_id)
        raise
