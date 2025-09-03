from fastapi import HTTPException

from app.singletons.logs_manager import LogsManager
from app.models.trigger_model import TriggerGraphRequestModel, TriggerGraphResponseModel
from app.models.state_status_enum import StateStatusEnum
from app.models.db.state import State
from app.models.db.store import Store
from app.models.db.run import Run
from app.models.db.graph_template_model import GraphTemplate
from app.models.node_template_model import NodeTemplate
import uuid

logger = LogsManager().get_logger()

def check_required_store_keys(graph_template: GraphTemplate, store: dict[str, str]) -> None:
    required_keys = set(graph_template.store_config.required_keys)
    provided_keys = set(store.keys())

    missing_keys = required_keys - provided_keys
    if missing_keys:
        raise HTTPException(status_code=400, detail=f"Missing store keys: {missing_keys}")
    

def construct_inputs(node: NodeTemplate, inputs: dict[str, str]) -> dict[str, str]:
    return {key: inputs.get(key, value) for key, value in node.inputs.items()}
    

async def trigger_graph(namespace_name: str, graph_name: str, body: TriggerGraphRequestModel, x_exosphere_request_id: str) -> TriggerGraphResponseModel:
    try:
        run_id = str(uuid.uuid4())
        logger.info(f"Triggering graph {graph_name} with run_id {run_id}", x_exosphere_request_id=x_exosphere_request_id)

        try:
            graph_template = await GraphTemplate.get(namespace_name, graph_name)
        except ValueError as e:
            logger.error(f"Graph template not found for namespace {namespace_name} and graph {graph_name}", x_exosphere_request_id=x_exosphere_request_id)
            if "Graph template not found" in str(e):
                raise HTTPException(status_code=404, detail=f"Graph template not found for namespace {namespace_name} and graph {graph_name}")
            else:
                raise e
            
        if not graph_template.is_valid():
            raise HTTPException(status_code=400, detail="Graph template is not valid")

        check_required_store_keys(graph_template, body.store)

        new_run = Run(
            run_id=run_id,
            namespace_name=namespace_name,
            graph_name=graph_name
        )
        await new_run.insert()

        new_stores = [
            Store(
                run_id=run_id,
                namespace=namespace_name,
                graph_name=graph_name,
                key=key,
                value=value
            ) for key, value in body.store.items()
        ]

        if len(new_stores) > 0:
            await Store.insert_many(new_stores)
        
        root = graph_template.get_root_node()

        new_state = State(
            node_name=root.node_name,
            namespace_name=namespace_name,
            identifier=root.identifier,
            graph_name=graph_name,
            run_id=run_id,
            status=StateStatusEnum.CREATED,
            inputs=construct_inputs(root, body.inputs),
            outputs={},
            error=None
        )
        await new_state.insert()

        return TriggerGraphResponseModel(
            status=StateStatusEnum.CREATED,
            run_id=run_id
        )

    except Exception as e:
        logger.error(f"Error triggering graph {graph_name} for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise e
