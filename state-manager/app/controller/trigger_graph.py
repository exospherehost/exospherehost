from fastapi import HTTPException

from app.singletons.logs_manager import LogsManager
from app.models.trigger_model import TriggerGraphRequestModel, TriggerGraphResponseModel
from app.models.state_status_enum import StateStatusEnum
from app.models.db.state import State
from app.models.db.store import Store
from app.models.db.graph_template_model import GraphTemplate
from app.models.node_template_model import NodeTemplate
import uuid

logger = LogsManager().get_logger()

def check_required_store_keys(graph_template: GraphTemplate, store: dict[str, str]) -> None:
    errors = []
    keys = set()
    
    for secret in graph_template.secrets.keys():
        if secret not in store.keys():
            errors.append(f"Missing store key: {secret}")
    
    for key in store.keys():
        if key in keys:
            errors.append(f"Duplicate store keys: {key}")
        keys.add(key)
    
    if errors:
        raise HTTPException(status_code=400, detail=f"Errors: {errors}")
    

def construct_inputs(node: NodeTemplate, inputs: dict[str, str]) -> dict[str, str]:
    constructed_inputs = {}
    for key, value in node.inputs.items():
        if key in inputs.keys():
            constructed_inputs[key] = inputs[key]
        else:
            constructed_inputs[key] = value
    return constructed_inputs
    

async def trigger_graph(namespace_name: str, graph_name: str, body: TriggerGraphRequestModel, x_exosphere_request_id: str) -> TriggerGraphResponseModel:
    try:
        run_id = str(uuid.uuid4())
        logger.info(f"Triggering graph {graph_name} with run_id {run_id}", x_exosphere_request_id=x_exosphere_request_id)

        graph_template = await GraphTemplate.get(namespace_name, graph_name)

        check_required_store_keys(graph_template, body.store)

        new_stores = []
        for key, value in body.store.items():
            new_store = Store(
                run_id=run_id,
                namespace=namespace_name,
                graph_name=graph_name,
                key=key,
                value=value
            )
            new_stores.append(new_store)

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
