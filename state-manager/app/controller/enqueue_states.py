from beanie.operators import In

from ..models.enqueue_request import EnqueueRequestModel
from ..models.enqueue_response import EnqueueResponseModel, StateModel
from ..models.db.state import State
from ..models.state_status_enum import StateStatusEnum

from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


async def enqueue_states(namespace_name: str, body: EnqueueRequestModel, x_exosphere_request_id: str) -> EnqueueResponseModel:
    
    try:
        logger.info(f"Enqueuing states for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        states = await State.find(
            State.namespace_name == namespace_name,
            State.status == StateStatusEnum.CREATED,
            In(State.node_name, body.nodes)
        ).limit(
            body.batch_size
        ).to_list()

        if states:
            await State.find(
                In(State.id, [state.id for state in states])
            ).set(
                {
                    "status": StateStatusEnum.QUEUED,
                }
            ) # type: ignore

        response = EnqueueResponseModel(
            count=len(states),
            namespace=namespace_name,
            status=StateStatusEnum.QUEUED,
            states=[
                StateModel(
                    state_id=str(state.id),
                    node_name=state.node_name,
                    identifier=state.identifier,
                    inputs=state.inputs,
                    created_at=state.created_at
                )
                for state in states
            ]
        )
        return response
    
    except Exception as e:
        logger.error(f"Error enqueuing states for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e