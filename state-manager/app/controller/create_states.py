from app.singletons.logs_manager import LogsManager
from app.models.create_models import CreateRequestModel, CreateResponseModel, ResponseStateModel
from app.models.state_status_enum import StateStatusEnum
from app.models.db.state import State

from beanie.operators import In
from bson import ObjectId

logger = LogsManager().get_logger()

async def create_states(namespace_name: str, body: CreateRequestModel, x_exosphere_request_id: str) -> CreateResponseModel:
    try:
        states = []
        logger.info(f"Creating states for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        
        for state in body.states:
            states.append(
                State(
                    node_name=state.node_name,
                    namespace_name=namespace_name,
                    status=StateStatusEnum.CREATED,
                    inputs=state.inputs,
                    outputs={},
                    error=None
                )
            )

        inserted_states = await State.insert_many(states)
        
        logger.info(f"Created states: {inserted_states.inserted_ids}", x_exosphere_request_id=x_exosphere_request_id)
        
        newStates = await State.find(
            In(State.id, [ObjectId(id) for id in inserted_states.inserted_ids])
        ).to_list()
        
        return CreateResponseModel(
            status=StateStatusEnum.CREATED,
            states=[ResponseStateModel(state_id=str(state.id), node_name=state.node_name, inputs=state.inputs, created_at=state.created_at) for state in newStates]
        )

    except Exception as e:
        logger.error(f"Error creating states for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise e