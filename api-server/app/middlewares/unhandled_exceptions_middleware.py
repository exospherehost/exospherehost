import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


class UnhandledExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                "unhandled global exception",
                error=str(e),
                traceback=traceback.format_exc(),
                path=request.url.path,
                method=request.method,
                x_exosphere_request_id=getattr(request.state, 'x_exosphere_request_id', None),
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "detail": "internal server error, please reach out to support team at nivedit@exosphere.host",
                },
            )
