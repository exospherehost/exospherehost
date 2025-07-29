from app.models.executed_models import ExecutedRequestModel, ExecutedResponseModel
from bson import ObjectId
from fastapi import HTTPException, status

from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()

async def executed_state(namespace_name: str, state_id: ObjectId, body: ExecutedRequestModel, x_exosphere_request_id: str) -> ExecutedResponseModel:

    try:
        logger.info(f"Executed state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        state = await State.find_one(State.id == state_id)
        if not state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")

        if state.status != StateStatusEnum.QUEUED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State is not queued")
        
        await State.find_one(State.id == state_id).set(
            {"status": StateStatusEnum.EXECUTED, "outputs": body.outputs}
        )

        return ExecutedResponseModel(status=StateStatusEnum.EXECUTED)

    except Exception as e:
        logger.error(f"Error executing state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e
