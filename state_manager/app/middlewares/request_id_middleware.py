import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # request part
        start_time = time.time()

        # get the request id from the header
        request_id = request.headers.get("x-exosphere-request-id")

        if not request_id:
            request_id = str(uuid.uuid4())
        else:
            try:
                uuid.UUID(request_id)
            except (ValueError, TypeError):
                request_id = str(uuid.uuid4())
        
        request.state.x_exosphere_request_id = request_id

        logger.info(
            "request received",
            x_exosphere_request_id=request_id,
            method=request.method,
            url=request.url.path,
        )

        # call the next middleware
        response = await call_next(request)

        # response part
        end_time = time.time()

        response_time = end_time - start_time
        response_time = response_time * 1000  # convert to milliseconds

        response.headers["x-exosphere-request-id"] = request_id

        logger.info(
            "request processed",
            x_exosphere_request_id=request_id,
            response_time=response_time,
            status_code=response.status_code,
        )

        return response
