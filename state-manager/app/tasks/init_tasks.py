# tasks to run when the server starts
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum
import asyncio

async def delete_old_triggers():
    await DatabaseTriggers.get_pymongo_collection().delete_many(
        {
            "trigger_status": {
                "$in": [TriggerStatusEnum.TRIGGERED, TriggerStatusEnum.FAILED]
            },
            "expires_at": None
        }
    )

async def init_tasks():
    await asyncio.gather(
        *[
            delete_old_triggers()
        ])