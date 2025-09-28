from datetime import datetime
from uuid import uuid4
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum
from app.singletons.logs_manager import LogsManager
from app.controller.trigger_graph import trigger_graph
from app.models.trigger_graph_model import TriggerGraphRequestModel
from pymongo import ReturnDocument

logger = LogsManager().get_logger()

async def get_due_triggers(cron_time: datetime) -> DatabaseTriggers | None:
    data = await DatabaseTriggers.get_pymongo_collection().find_one_and_update(
        {
            "trigger_time": {"$lte": cron_time},
            "trigger_status": TriggerStatusEnum.PENDING
        },
        {
            "$set": {"trigger_status": TriggerStatusEnum.TRIGGERED}
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

async def create_next_triggers(trigger: DatabaseTriggers):
    pass

async def trigger_cron():
    cron_time = datetime.now()
    logger.info(f"starting trigger_cron: {cron_time}")

    while(trigger:= await get_due_triggers(cron_time)):
        await call_trigger_graph(trigger)
        await create_next_triggers(trigger)