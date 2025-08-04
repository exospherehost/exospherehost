"""
main file for exosphere apis
"""
import os
from beanie import init_beanie
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
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
 
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # begaining of the server
    logger = LogsManager().get_logger()
    logger.info("server starting")

    # initializing beanie
    client = AsyncMongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DATABASE_NAME", "exosphere-state-manager")]
    await init_beanie(db, document_models=[State, Namespace, GraphTemplate, RegisteredNode])
    logger.info("beanie dbs initialized")

    # initialize secret
    secret = os.getenv("STATE_MANAGER_SECRET")
    if not secret:
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

# this middleware should be the first one
app.add_middleware(RequestIdMiddleware)
app.add_middleware(UnhandledExceptionsMiddleware)


@app.get("/health")
def health() -> dict:
    return {"message": "OK"}

app.include_router(router)