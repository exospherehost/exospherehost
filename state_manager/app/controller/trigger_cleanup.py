# app/controller/trigger_cleanup.py

from datetime import datetime, timedelta, timezone
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum
from app.singletons.logs_manager import LogsManager
from app.config.settings import get_settings
import asyncio

logger = LogsManager().get_logger()

async def cleanup_old_triggers():
    """
    Remove CANCELLED or TRIGGERED triggers older than `trigger_retention_days`.
    """
    retention_days = getattr(get_settings(), "trigger_retention_days", 30)
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)  # UTC-aware

    result = await DatabaseTriggers.get_pymongo_collection().delete_many({
        "trigger_status": {"$in": [TriggerStatusEnum.CANCELLED, TriggerStatusEnum.TRIGGERED]},
        "trigger_time": {"$lte": cutoff_time}
    })

    logger.info(f"Cleanup complete. Deleted {result.deleted_count} old triggers.")

async def start_periodic_cleanup():
    """
    Periodically run cleanup every `cleanup_interval_minutes`.
    """
    interval = getattr(get_settings(), "cleanup_interval_minutes", 60)  # default 1 hour
    logger.info(f"Starting periodic trigger cleanup every {interval} minutes.")
    
    while True:
        try:
            await cleanup_old_triggers()
        except Exception as e:
            logger.error(f"Error during trigger cleanup: {e}")
        await asyncio.sleep(interval * 60)
