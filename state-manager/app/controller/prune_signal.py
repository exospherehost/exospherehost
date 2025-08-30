from app.models.signal_models import PruneRequestModel, SignalResponseModel
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()

async def prune_signal(namespace_name: str, state_id: PydanticObjectId, body: PruneRequestModel, x_exosphere_request_id: str) -> SignalResponseModel:

    try:
        logger.info(f"Received prune signal for state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        state = await State.find_one(State.id == state_id, State.namespace_name == namespace_name)

        if not state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")
        
        if state.status != StateStatusEnum.QUEUED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State is not queued")
        
        state.status = StateStatusEnum.PRUNED
        state.data = body.data
        await state.save()

        return SignalResponseModel(status=StateStatusEnum.PRUNED, enqueue_after=state.enqueue_after)

    except Exception as e:
        logger.error(f"Error pruning state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise