from app.models.executed_models import ExecutedRequestModel, ExecutedResponseModel
from bson import ObjectId
from fastapi import HTTPException, status, BackgroundTasks

from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager
from app.tasks.create_next_state import create_next_state

logger = LogsManager().get_logger()

async def executed_state(namespace_name: str, state_id: ObjectId, body: ExecutedRequestModel, x_exosphere_request_id: str, background_tasks: BackgroundTasks) -> ExecutedResponseModel:

    try:
        logger.info(f"Executed state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        state = await State.find_one(State.id == state_id)
        if not state:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")

        if state.status != StateStatusEnum.QUEUED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State is not queued")
        
        if len(body.outputs) == 0:
            await State.find_one(State.id == state_id).set(
                {"status": StateStatusEnum.EXECUTED, "outputs": {}, "parents": {**state.parents, state.identifier: ObjectId(state.id)}}
            )

            background_tasks.add_task(create_next_state, state)

        else:
            await State.find_one(State.id == state_id).set(
                {"status": StateStatusEnum.EXECUTED, "outputs": body.outputs[0], "parents": {**state.parents, state.identifier: ObjectId(state.id)}}
            )
            background_tasks.add_task(create_next_state, state)

            for output in body.outputs[1:]:
                new_state = State(
                    node_name=state.node_name,
                    namespace_name=state.namespace_name,
                    identifier=state.identifier,
                    graph_name=state.graph_name,
                    status=StateStatusEnum.CREATED,
                    inputs=state.inputs,
                    outputs=output,
                    error=None,
                    parents={
                        **state.parents,
                        state.identifier: ObjectId(state.id)
                    }
                )
                await new_state.save()
                background_tasks.add_task(create_next_state, new_state)

        return ExecutedResponseModel(status=StateStatusEnum.EXECUTED)

    except Exception as e:
        logger.error(f"Error executing state {state_id} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise e
