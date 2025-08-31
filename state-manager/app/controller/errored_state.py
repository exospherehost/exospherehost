from app.models.errored_models import ErroredRequestModel, ErroredResponseModel
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager
from app.models.retry_policy_model import RetryPolicyModel, RetryMethod
from app.models.db.graph_template_model import GraphTemplate

logger = LogsManager().get_logger()

def _calculate_enqueue_after(retry_policy: RetryPolicyModel, retry_count: int) -> int:
    # convert seconds to milliseconds
    if retry_policy.method == RetryMethod.FIXED:
        return (retry_policy.backoff_factor * 1000)
    elif retry_policy.method == RetryMethod.LINEAR:
        return (retry_policy.backoff_factor * retry_count) * 1000
    elif retry_policy.method == RetryMethod.EXPONENTIAL:
        return (retry_policy.backoff_factor ** retry_count) * 1000
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid retry method")

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
        
        graph_template = await GraphTemplate.get(namespace_name, state.graph_name)

        retry_created = False

        if state.retry_count < graph_template.retry_policy.max_retries:
            retry_state = State(
                node_name=state.node_name,
                namespace_name=state.namespace_name,
                identifier=state.identifier,
                graph_name=state.graph_name,
                run_id=state.run_id,
                status=StateStatusEnum.CREATED,
                inputs=state.inputs,
                outputs=state.outputs,
                error=body.error,
                parents=state.parents,
                does_unites=state.does_unites,
                enqueue_after=state.enqueue_after + _calculate_enqueue_after(graph_template.retry_policy, state.retry_count + 1),
                retry_count=state.retry_count + 1
            )
            retry_state = await retry_state.insert()
            logger.info(f"Retry state {retry_state.id} created for state {state_id}", x_exosphere_request_id=x_exosphere_request_id)
            retry_created = True

        state.status = StateStatusEnum.ERRORED
        state.error = body.error
        await state.save()

        return ErroredResponseModel(status=StateStatusEnum.ERRORED, retry_created=retry_created)

    except Exception as e:
        logger.error(f"Error errored state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e