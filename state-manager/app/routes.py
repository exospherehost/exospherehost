from fastapi import APIRouter, status, Request, Depends, HTTPException
from uuid import uuid4

from app.utils.check_secret import check_api_key
from app.singletons.logs_manager import LogsManager

from .models.enqueue_response import EnqueueResponseModel
from .models.enqueue_request import EnqueueRequestModel
from .controller.enqueue_states import enqueue_states

from .models.create_models import CreateRequestModel, CreateResponseModel
from .controller.create_states import create_states


logger = LogsManager().get_logger()

router = APIRouter(prefix="/v0/namespace/{namespace_name}/states", tags=["state"])


@router.post(
    "/enqueue",
    response_model=EnqueueResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="State enqueued on node queue successfully"
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
    "/create",
    response_model=CreateResponseModel,
    status_code=status.HTTP_200_OK,
    response_description="States created successfully"
)
async def create_state(namespace_name: str, body: CreateRequestModel, request: Request, api_key: str = Depends(check_api_key)):

    x_exosphere_request_id = getattr(request.state, "x_exosphere_request_id", str(uuid4()))

    if api_key:
        logger.info(f"API key is valid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
    else:
        logger.error(f"API key is invalid for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await create_states(namespace_name, body, x_exosphere_request_id)