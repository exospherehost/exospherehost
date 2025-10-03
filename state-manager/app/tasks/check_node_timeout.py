import time
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager
from app.config.settings import get_settings

logger = LogsManager().get_logger()


async def check_node_timeout():
    try:
        settings = get_settings()
        timeout_ms = settings.node_timeout_minutes * 60 * 1000
        current_time_ms = int(time.time() * 1000)
        timeout_threshold = current_time_ms - timeout_ms

        logger.info(f"Checking for timed out nodes with threshold: {timeout_threshold}")

        result = await State.get_pymongo_collection().update_many(
            {
                "status": StateStatusEnum.QUEUED,
                "queued_at": {"$ne": None, "$lte": timeout_threshold}
            },
            {
                "$set": {
                    "status": StateStatusEnum.TIMEDOUT,
                    "error": f"Node execution timed out after {settings.node_timeout_minutes} minutes"
                }
            }
        )

        if result.modified_count > 0:
            logger.info(f"Marked {result.modified_count} states as TIMEDOUT")
        
    except Exception:
        logger.error("Error checking node timeout", exc_info=True)
