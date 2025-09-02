from ..models.state_list_models import RunsResponse
from ..models.db.state import State

from ..singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()

async def get_runs(namespace_name: str, page: int, size: int, x_exosphere_request_id: str) -> RunsResponse:
    try:
        logger.info(f"Getting runs for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        
        state_collection = State.get_pymongo_collection()

        

    except Exception as e:
        logger.error(f"Error getting runs for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise