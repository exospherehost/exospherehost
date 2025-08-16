from fastapi import APIRouter, status, Request, Depends, HTTPException, BackgroundTasks
from uuid import uuid4
from beanie import PydanticObjectId

from app.utils.check_secret import check_api_key
from app.singletons.logs_manager import LogsManager

from .models.enqueue_response import EnqueueResponseModel
from .models.enqueue_request import EnqueueRequestModel
from .controller.enqueue_states import enqueue_states

from .models.create_models import CreateRequestModel, CreateResponseModel, TriggerGraphRequestModel, TriggerGraphResponseModel
from .controller.create_states import create_states, trigger_graph

from .models.executed_models import ExecutedRequestModel, ExecutedResponseModel
from .controller.executed_state import executed_state

from .models.errored_models import ErroredRequestModel, ErroredResponseModel
from .controller.errored_state import errored_state

from .models.graph_models import UpsertGraphTemplateRequest, UpsertGraphTemplateResponse
from .controller.upsert_graph_template import upsert_graph_template as upsert_graph_template_controller
from .controller.get_graph_template import get_graph_template as get_graph_template_controller

from .models.register_nodes_request import RegisterNodesRequestModel
from .models.register_nodes_response import RegisterNodesResponseModel
from .controller.register_nodes import register_nodes

from .models.secrets_response import SecretsResponseModel
from .controller.get_secrets import get_secrets

from .models.list_models import ListRegisteredNodesResponse, ListGraphTemplatesResponse
from .controller.list_registered_nodes import list_registered_nodes
from .controller.list_graph_templates import list_graph_templates

from .models.state_list_models import StatesByRunIdResponse, CurrentStatesResponse
from .controller.get_states_by_run_id import get_states_by_run_id
from .controller.get_current_states import get_current_states

logger = LogsManager().get_logger()

router = APIRouter(prefix="/v0/namespace/{namespace_name}")


@router.post(
    "/states/enqueue",
    response_model=EnqueueResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="State enqueued on node queue successfully",
    tags=["state"]
)
async def enqueue_state(namespace_name: str, body: EnqueueRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await enqueue_states(namespace_name, body, x_exosphere_request_id)


@router.post(
    "/graph/{graph_name}/trigger",
    response_model=TriggerGraphResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="Graph triggered successfully with new run ID",
    tags=["graph"]
)
async def trigger_graph_route(namespace_name: str, graph_name: str, body: TriggerGraphRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await trigger_graph(namespace_name, graph_name, body, x_exosphere_request_id)


@router.post(
    "/graph/{graph_name}/states/create",
    response_model=CreateResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="States created successfully",
    tags=["state"]
)
async def create_state(namespace_name: str, graph_name: str, body: CreateRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await create_states(namespace_name, graph_name, body, x_exosphere_request_id)


@router.post(
    "/states/{state_id}/executed",
    response_model=ExecutedResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="State executed successfully",
    tags=["state"]
)
async def executed_state_route(namespace_name: str, state_id: str, body: ExecutedRequestModel, request: Request, background_tasks: BackgroundTasks, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await executed_state(namespace_name, PydanticObjectId(state_id), body, x_exosphere_request_id, background_tasks)


@router.post(
    "/states/{state_id}/errored",
    response_model=ErroredResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="State errored successfully",
    tags=["state"]
)
async def errored_state_route(namespace_name: str, state_id: str, body: ErroredRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await errored_state(namespace_name, PydanticObjectId(state_id), body, x_exosphere_request_id)


@router.put(
    "/graph/{graph_name}",
    response_model=UpsertGraphTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Graph template upserted successfully",
    tags=["graph"]
)   
async def upsert_graph_template(namespace_name: str, graph_name: str, body: UpsertGraphTemplateRequest, request: Request, background_tasks: BackgroundTasks, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await upsert_graph_template_controller(namespace_name, graph_name, body, x_exosphere_request_id, background_tasks)


@router.get(
    "/graph/{graph_name}",
    response_model=UpsertGraphTemplateResponse,
    status_code=status.HTTP_200_OK,
    response_description="Graph template retrieved successfully",
    tags=["graph"]
)
async def get_graph_template(namespace_name: str, graph_name: str, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await get_graph_template_controller(namespace_name, graph_name, x_exosphere_request_id)


@router.put(
    "/nodes/",
    response_model=RegisterNodesResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="Nodes registered successfully",
    tags=["nodes"]
)
async def register_nodes_route(namespace_name: str, body: RegisterNodesRequestModel, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await register_nodes(namespace_name, body, x_exosphere_request_id)


@router.get(
    "/state/{state_id}/secrets",
    response_model=SecretsResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="Secrets retrieved successfully",
    tags=["state"]
)
async def get_secrets_route(namespace_name: str, state_id: str, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info("API key is valid", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error("API key is invalid", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    
    return await get_secrets(namespace_name, state_id, x_exosphere_request_id)


@router.get(
    "/nodes/",
    response_model=ListRegisteredNodesResponse,
    status_code=status.HTTP_200_OK,
    response_description="Registered nodes listed successfully",
    tags=["nodes"]
)
async def list_registered_nodes_route(namespace_name: str, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    nodes = await list_registered_nodes(namespace_name, x_exosphere_request_id)
    return ListRegisteredNodesResponse(
        namespace=namespace_name,
        count=len(nodes),
        nodes=nodes
    )


@router.get(
    "/graphs/",
    response_model=ListGraphTemplatesResponse,
    status_code=status.HTTP_200_OK,
    response_description="Graph templates listed successfully",
    tags=["graph"]
)
async def list_graph_templates_route(namespace_name: str, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    templates = await list_graph_templates(namespace_name, x_exosphere_request_id)
    return ListGraphTemplatesResponse(
        namespace=namespace_name,
        count=len(templates),
        templates=templates
    )


@router.get(
    "/states/",
    response_model=CurrentStatesResponse,
    status_code=status.HTTP_200_OK,
    response_description="Current states listed successfully",
    tags=["state"]
)
async def get_current_states_route(namespace_name: str, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    states = await get_current_states(namespace_name, x_exosphere_request_id)
    
    # Convert states to response format
    state_items = []
    run_ids = set()
    
    for state in states:
        # Convert ObjectId parents to strings
        parents_dict = {k: str(v) for k, v in state.parents.items()}
        
        state_items.append({
            "id": str(state.id),
            "node_name": state.node_name,
            "namespace_name": state.namespace_name,
            "identifier": state.identifier,
            "graph_name": state.graph_name,
            "run_id": state.run_id,
            "status": state.status,
            "inputs": state.inputs,
            "outputs": state.outputs,
            "error": state.error,
            "parents": parents_dict,
            "created_at": state.created_at,
            "updated_at": state.updated_at
        })
        run_ids.add(state.run_id)
    
    return CurrentStatesResponse(
        namespace=namespace_name,
        count=len(states),
        states=state_items,
        run_ids=list(run_ids)
    )


@router.get(
    "/states/run/{run_id}",
    response_model=StatesByRunIdResponse,
    status_code=status.HTTP_200_OK,
    response_description="States by run ID listed successfully",
    tags=["state"]
)
async def get_states_by_run_id_route(namespace_name: str, run_id: str, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    states = await get_states_by_run_id(namespace_name, run_id, x_exosphere_request_id)
    
    # Convert states to response format
    state_items = []
    
    for state in states:
        # Convert ObjectId parents to strings
        parents_dict = {k: str(v) for k, v in state.parents.items()}
        
        state_items.append({
            "id": str(state.id),
            "node_name": state.node_name,
            "namespace_name": state.namespace_name,
            "identifier": state.identifier,
            "graph_name": state.graph_name,
            "run_id": state.run_id,
            "status": state.status,
            "inputs": state.inputs,
            "outputs": state.outputs,
            "error": state.error,
            "parents": parents_dict,
            "created_at": state.created_at,
            "updated_at": state.updated_at
        })
    
    return StatesByRunIdResponse(
        namespace=namespace_name,
        run_id=run_id,
        count=len(states),
        states=state_items
    )