from datetime import datetime
from uuid import uuid4
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum, TriggerTypeEnum
from app.singletons.logs_manager import LogsManager
from app.controller.trigger_graph import trigger_graph
from app.models.trigger_graph_model import TriggerGraphRequestModel
from pymongo import ReturnDocument
from app.config.settings import get_settings
import croniter
import asyncio

logger = LogsManager().get_logger()

async def get_due_triggers(cron_time: datetime) -> DatabaseTriggers | None:
    data = await DatabaseTriggers.get_pymongo_collection().find_one_and_update(
        {
            "trigger_time": {"$lte": cron_time},
            "trigger_status": TriggerStatusEnum.PENDING
        },
        {
            "$set": {"trigger_status": TriggerStatusEnum.TRIGGERING}
        },
        return_document=ReturnDocument.AFTER
    )
    return DatabaseTriggers(**data) if data else None

async def call_trigger_graph(trigger: DatabaseTriggers):
    await trigger_graph(
        namespace_name=trigger.namespace,
        graph_name=trigger.graph_name,
        body=TriggerGraphRequestModel(),
        x_exosphere_request_id=str(uuid4())
    )

async def mark_as_failed(trigger: DatabaseTriggers):
    await DatabaseTriggers.get_pymongo_collection().update_one(
        {"_id": trigger.id},
        {"$set": {"trigger_status": TriggerStatusEnum.FAILED}}
    )

async def create_next_triggers(trigger: DatabaseTriggers, cron_time: datetime):
    assert trigger.expression is not None
    iter = croniter.croniter(trigger.expression, cron_time)
    next_trigger_time = iter.get_next(datetime)

    await DatabaseTriggers(
        type=TriggerTypeEnum.CRON,
        expression=trigger.expression,
        graph_name=trigger.graph_name,
        namespace=trigger.namespace,
        trigger_time=next_trigger_time,
        trigger_status=TriggerStatusEnum.PENDING
    ).insert()

async def mark_as_triggered(trigger: DatabaseTriggers):
    await DatabaseTriggers.get_pymongo_collection().update_one(
        {"_id": trigger.id},
        {"$set": {"trigger_status": TriggerStatusEnum.TRIGGERED}}
    )

async def handle_trigger(cron_time: datetime):
    while(trigger:= await get_due_triggers(cron_time)):
        try:
            await call_trigger_graph(trigger)
            await create_next_triggers(trigger, cron_time)
            await mark_as_triggered(trigger)
        except Exception as e:
            await mark_as_failed(trigger)
            logger.error(f"Error calling trigger graph: {e}")

async def trigger_cron():
    cron_time = datetime.now()
    logger.info(f"starting trigger_cron: {cron_time}")
    await asyncio.gather(*[handle_trigger(cron_time) for _ in range(get_settings().trigger_workers)])