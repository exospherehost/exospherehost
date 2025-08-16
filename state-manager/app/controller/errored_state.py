from app.models.errored_models import ErroredRequestModel, ErroredResponseModel
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()

async def errored_state(namespace_name: str, state_id: PydanticObjectId, body: ErroredRequestModel, x_exosphere_request_id: str) -> ErroredResponseModel:

    try:
        logger.info(f"Errored state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        state = await State.find_one(State.id == state_id)
        if not state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")
        
        if state.status != StateStatusEnum.QUEUED and state.status != StateStatusEnum.EXECUTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State is not queued or executed")
        
        if state.status == StateStatusEnum.EXECUTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State is already executed")
        
        state.status = StateStatusEnum.ERRORED
        state.error = body.error
        await state.save()

        return ErroredResponseModel(status=StateStatusEnum.ERRORED)

    except Exception as e:
        logger.error(f"Error errored state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e