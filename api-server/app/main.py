"""
main file for exosphere apis
"""
import os
from beanie import init_beanie
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# injecting singletons
from .singletons.logs_manager import LogsManager

# injecting middlewares
from .middlewares.unhandled_exceptions_middleware import (
    UnhandledExceptionsMiddleware,
)
from .middlewares.request_id_middleware import RequestIdMiddleware

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # begaining of the server
    logger = LogsManager().get_logger()
    logger.info("server starting")

    # initializing beanie
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DATABASE_NAME")]
    await init_beanie(db, document_models=[])
    logger.info("beanie dbs initialized")

    # main logic of the server
    yield

    # end of the server
    logger.info("server shutting down")


app = FastAPI(lifespan=lifespan)

# this middleware should be the first one
app.add_middleware(RequestIdMiddleware)

# this middleware should be the last one
app.add_middleware(UnhandledExceptionsMiddleware)


@app.get("/health-check")
def health() -> dict:
    return {"message": "OK"}
