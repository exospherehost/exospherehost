# tasks to run when the server starts
from datetime import datetime, timedelta, timezone
import asyncio

from app.config.settings import get_settings
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


async def delete_old_triggers():
    settings = get_settings()
    retention_hours = settings.trigger_retention_hours
    expires_at = datetime.now(timezone.utc) + timedelta(hours=retention_hours)

    # Use the same filter used before by delete_many()
    filter_query = {
        "trigger_status": {
            "$in": [TriggerStatusEnum.TRIGGERED, TriggerStatusEnum.FAILED]
        },
        "expires_at": None
    }

    logger.info(
        f"Init task marking triggers CANCELLED for filter={filter_query}, "
        f"expires_at={expires_at.isoformat()}"
    )

    await DatabaseTriggers.get_pymongo_collection().update_many(
        filter_query,
        {
            "$set": {
                "trigger_status": TriggerStatusEnum.CANCELLED,
                "expires_at": expires_at,
            }
        },
    )


async def init_tasks():
    await asyncio.gather(
        *[
            delete_old_triggers(),
        ]
    )
