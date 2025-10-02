from app.singletons.logs_manager import LogsManager
from app.models.secrets_response import SecretsResponseModel
from app.models.db.state import State
from app.models.db.graph_template_model import GraphTemplate

logger = LogsManager().get_logger()


async def get_secrets(namespace_name: str, state_id: str, x_exosphere_request_id: str) -> SecretsResponseModel:
    """
    Get secrets for a specific state.
    
    Args:
        namespace_name (str): The namespace name
        state_id (str): The state ID
        x_exosphere_request_id (str): Request ID for logging
        
    Returns:
        SecretsResponseModel: The secrets for the state
        
    Raises:
        ValueError: If state is not found or graph template is not found
    """
    try:
        # Get the state
        state = await State.get(state_id)
        if not state:
            logger.error(f"State {state_id} not found", x_exosphere_request_id=x_exosphere_request_id)
            raise ValueError(f"State {state_id} not found")
        
        # Verify the state belongs to the namespace
        if state.namespace_name != namespace_name:
            logger.error(f"State {state_id} does not belong to namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
            raise ValueError(f"State {state_id} does not belong to namespace {namespace_name}")
        
        # Get the graph template to retrieve secrets
        graph_template = await GraphTemplate.find_one(
            GraphTemplate.name == state.graph_name,
            GraphTemplate.namespace == namespace_name
        )
        
        if not graph_template:
            logger.error(f"Graph template {state.graph_name} not found in namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
            raise ValueError(f"Graph template {state.graph_name} not found in namespace {namespace_name}")
        
        # Get the secrets from the graph template
        secrets_dict = graph_template.get_secrets()
        
        logger.info(f"Retrieved {len(secrets_dict)} secrets for state {state_id}", x_exosphere_request_id=x_exosphere_request_id)
        
        return SecretsResponseModel(secrets=secrets_dict)
        
    except Exception as e:
        logger.error(f"Error getting secrets for state {state_id}: {str(e)}", x_exosphere_request_id=x_exosphere_request_id)
        raise e 