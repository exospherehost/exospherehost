from fastapi import HTTPException

from app.singletons.logs_manager import LogsManager
from app.models.create_models import CreateRequestModel, CreateResponseModel, ResponseStateModel, TriggerGraphRequestModel, TriggerGraphResponseModel
from app.models.state_status_enum import StateStatusEnum
from app.models.db.state import State
from app.models.db.graph_template_model import GraphTemplate
from app.models.node_template_model import NodeTemplate

from beanie.operators import In
from beanie import PydanticObjectId
import uuid

logger = LogsManager().get_logger()


def get_node_template(graph_template: GraphTemplate, identifier: str) -> NodeTemplate:
    node = graph_template.get_node_by_identifier(identifier)
    if not node:
        raise HTTPException(status_code=404, detail="Node template not found")
    return node


async def trigger_graph(namespace_name: str, graph_name: str, body: TriggerGraphRequestModel, x_exosphere_request_id: str) -> TriggerGraphResponseModel:
    try:
        # Generate a new run ID for this graph execution
        run_id = str(uuid.uuid4())
        logger.info(f"Triggering graph {graph_name} with run_id {run_id}", x_exosphere_request_id=x_exosphere_request_id)

        # Create a CreateRequestModel with the generated run_id
        create_request = CreateRequestModel(
            run_id=run_id,
            states=body.states
        )

        # Call the existing create_states function
        create_response = await create_states(namespace_name, graph_name, create_request, x_exosphere_request_id)

        # Return the trigger response with the generated run_id
        return TriggerGraphResponseModel(
            run_id=run_id,
            status=create_response.status,
            states=create_response.states
        )

    except Exception as e:
        logger.error(f"Error triggering graph {graph_name} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise e


async def create_states(namespace_name: str, graph_name: str, body: CreateRequestModel, x_exosphere_request_id: str) -> CreateResponseModel:
    try:
        states = []
        logger.info(f"Creating states for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        graph_template = await GraphTemplate.find_one(GraphTemplate.name == graph_name, GraphTemplate.namespace == namespace_name)
        if not graph_template:
            raise HTTPException(status_code=404, detail="Graph template not found")
        
        for state in body.states:

            node_template = get_node_template(graph_template, state.identifier)

            states.append(
                State(
                    identifier=state.identifier,
                    node_name=node_template.node_name,
                    namespace_name=node_template.namespace,
                    graph_name=graph_name,
                    run_id=body.run_id,
                    status=StateStatusEnum.CREATED,
                    inputs=state.inputs,
                    outputs={},
                    error=None
                )
            )

        inserted_states = await State.insert_many(states)
        
        logger.info(f"Created states: {inserted_states.inserted_ids}", x_exosphere_request_id=x_exosphere_request_id)
        
        newStates = await State.find(
            In(State.id, [PydanticObjectId(id) for id in inserted_states.inserted_ids])
        ).to_list()
        
        return CreateResponseModel(
            status=StateStatusEnum.CREATED,
            states=[ResponseStateModel(state_id=str(state.id), identifier=state.identifier, node_name=state.node_name, graph_name=state.graph_name, run_id=state.run_id, inputs=state.inputs, created_at=state.created_at) for state in newStates]
        )

    except Exception as e:
        logger.error(f"Error creating states for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise e