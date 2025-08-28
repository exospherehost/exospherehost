"""
main file for exosphere state manager
"""
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient

# injecting singletons
from .singletons.logs_manager import LogsManager

# injecting middlewares
from .middlewares.unhandled_exceptions_middleware import (
    UnhandledExceptionsMiddleware,
)
from .middlewares.request_id_middleware import RequestIdMiddleware

# injecting models
from .models.db.state import State
from .models.db.namespace import Namespace
from .models.db.graph_template_model import GraphTemplate
from .models.db.registered_node import RegisteredNode

# injecting routes
from .routes import router

# importing CORS config
from .config.cors import get_cors_config
from .config.settings import get_settings
 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # begaining of the server
    logger = LogsManager().get_logger()
    logger.info("server starting")

    # Get settings
    settings = get_settings()

    # initializing beanie
    client = AsyncMongoClient(settings.mongo_uri)
    db = client[settings.mongo_database_name]
    await init_beanie(db, document_models=[State, Namespace, GraphTemplate, RegisteredNode])
    logger.info("beanie dbs initialized")

    # initialize secret
    if not settings.state_manager_secret:
        raise ValueError("STATE_MANAGER_SECRET is not set")
    logger.info("secret initialized")

    # main logic of the server
    yield

    # end of the server
    logger.info("server shutting down")


app = FastAPI(
    lifespan=lifespan,
    title="Exosphere State Manager",
    description="Exosphere State Manager",
    version="0.1.0",
    contact={
        "name": "Nivedit Jain (Founder exosphere.host)",
        "email": "nivedit@exosphere.host",
    },
    license_info={
        "name": "Elastic License 2.0 (ELv2)",
        "url": "https://github.com/exospherehost/exosphere-api-server/blob/main/LICENSE",
    },
)

# Add middlewares in inner-to-outer order (last added runs first on request):  
# 1) UnhandledExceptions (inner)  
app.add_middleware(UnhandledExceptionsMiddleware)  
# 2) Request ID (middle)  
app.add_middleware(RequestIdMiddleware)  
# 3) CORS (outermost)  
app.add_middleware(CORSMiddleware, **get_cors_config())  


@app.get("/health")
def health() -> dict:
    return {"message": "OK"}

app.include_router(router)