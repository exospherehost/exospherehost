from fastapi import APIRouter, status, Request, Depends, HTTPException
from uuid import uuid4
from bson import ObjectId

from app.utils.check_secret import check_api_key
from app.singletons.logs_manager import LogsManager

from .models.enqueue_response import EnqueueResponseModel
from .models.enqueue_request import EnqueueRequestModel
from .controller.enqueue_states import enqueue_states

from .models.create_models import CreateRequestModel, CreateResponseModel
from .controller.create_states import create_states

from .models.executed_models import ExecutedRequestModel, ExecutedResponseModel
from .controller.executed_state import executed_state

from .models.errored_models import ErroredRequestModel, ErroredResponseModel
from .controller.errored_state import errored_state

from .models.graph_models import UpsertGraphTemplateRequest, UpsertGraphTemplateResponse
from .controller.upsert_graph_template import upsert_graph_template as upsert_graph_template_controller

from .models.register_nodes_request import RegisterNodesRequestModel
from .models.register_nodes_response import RegisterNodesResponseModel
from .controller.register_nodes import register_nodes



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
    "/states/create",
    response_model=CreateResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="States created successfully",
    tags=["state"]
)
async def create_state(namespace_name: str, body: CreateRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await create_states(namespace_name, body, x_exosphere_request_id)


@router.post(
    "/states/{state_id}/executed",
    response_model=ExecutedResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="State executed successfully",
    tags=["state"]
)
async def executed_state_route(namespace_name: str, state_id: str, body: ExecutedRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await executed_state(namespace_name, ObjectId(state_id), body, x_exosphere_request_id)


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

    return await errored_state(namespace_name, ObjectId(state_id), body, x_exosphere_request_id)


@router.put(
    "/graph-templates/{graph_name}",
    response_model=UpsertGraphTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Graph template upserted successfully",
    tags=["graph"]
)   
async def upsert_graph_template(namespace_name: str, graph_name: str, body: UpsertGraphTemplateRequest, request: Request, api_key: str = Depends(check_api_key)):
    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await upsert_graph_template_controller(namespace_name, graph_name, body, x_exosphere_request_id)


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