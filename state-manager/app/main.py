"""
main file for exosphere state manager
"""
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
import logging
from typing import List, Optional

# injecting singletons
from .singletons.logs_manager import LogsManager

# injecting middlewares
from .middlewares.unhandled_exceptions_middleware import (
    UnhandledExceptionsMiddleware,
)
from .middlewares.request_id_middleware import RequestIdMiddleware

# injecting models
from .models.db.state import State
from .models.db.graph_template_model import GraphTemplate
from .models.db.registered_node import RegisteredNode
from .models.db.store import Store
from .models.db.run import Run
from .models.db.trigger import DatabaseTriggers

# injecting routes
from .routes import router, global_router

# importing CORS config
from .config.cors import get_cors_config
from .config.settings import get_settings

# importing database health check function
from .utils.check_database_health import check_database_health

# scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks.trigger_cron import trigger_cron

# init tasks
from .tasks.init_tasks import init_tasks

# Define models list
DOCUMENT_MODELS = [State, GraphTemplate, RegisteredNode, Store, Run, DatabaseTriggers]

scheduler = AsyncIOScheduler()

# use module logger (LogsManager also produces app logs)
logger = logging.getLogger(__name__)


async def ensure_ttl_indexes(db, ttl_days: int = 30, collections: Optional[List[str]] = None):
    """
    Ensure TTL indexes exist on the specified collections.
    
    Creates a TTL (Time To Live) index that automatically deletes documents after
    they reach a certain age based on the 'created_at' timestamp field.

    Args:
        db: async pymongo Database instance (from AsyncMongoClient)
        ttl_days: number of days after which documents should expire (default: 30)
        collections: list of collection names to apply TTL to (defaults to ['runs'])
    """
    if collections is None:
        collections = ["runs"]

    ttl_seconds = int(ttl_days) * 24 * 3600
    timestamp_field = "created_at"

    for coll_name in collections:
        try:
            coll = db.get_collection(coll_name)
            
            # create_index is idempotent: it will reuse existing identical index
            # We use ascending order (1) — TTL index must be single-field.
            await coll.create_index(
                [(timestamp_field, 1)], 
                expireAfterSeconds=ttl_seconds,
                name=f"ttl_{timestamp_field}_index"
            )
            
            logger.info(
                "Successfully ensured TTL index on collection '%s' with field '%s' (expireAfterSeconds=%d, ttl_days=%d)",
                coll_name,
                timestamp_field,
                ttl_seconds,
                ttl_days
            )
        except Exception as e:
            # Log error but don't crash the server
            logger.error(
                "Failed to create TTL index on collection '%s' with field '%s': %s",
                coll_name,
                timestamp_field,
                e,
                exc_info=True
            )

    logger.info("TTL index setup completed for collections: %s", collections)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # beginning of the server
    log = LogsManager().get_logger()
    log.info("server starting")

    # Get settings
    settings = get_settings()

    # initializing beanie (and Mongo client)
    client = AsyncMongoClient(settings.mongo_uri)
    db = client[settings.mongo_database_name]

    # Initialize beanie models (this registers document models / collections)
    await init_beanie(db, document_models=DOCUMENT_MODELS)
    log.info("beanie dbs initialized")

    # --- ENSURE TTL INDEXES (conservative, before init_tasks) ---
    # Start with 'runs' only to be safe. Add other collections once you confirm.
    log.info("Starting TTL index creation...")
    try:
        await ensure_ttl_indexes(db, ttl_days=30, collections=["runs"])
        log.info("TTL index creation completed successfully")
    except Exception as e:
        # By default we log and continue. If you want fail-fast, replace with `raise`.
        log.exception("Error while ensuring TTL indexes: %s", e)

    # performing init tasks
    log.info("Starting init tasks...")
    await init_tasks()
    log.info("init tasks completed")

    # initialize secret
    if not settings.state_manager_secret:
        # this is critical — fail immediately
        raise ValueError("STATE_MANAGER_SECRET is not set")
    log.info("secret initialized")

    # perform database health check
    await check_database_health(DOCUMENT_MODELS)

    # schedule the cron job
    scheduler.add_job(
        trigger_cron,
        CronTrigger.from_crontab("* * * * *"),
        replace_existing=True,
        misfire_grace_time=60,
        coalesce=True,
        max_instances=1,
        id="every_minute_task",
    )
    scheduler.start()

    # main logic of the server
    yield

    # end of the server
    await client.close()
    scheduler.shutdown()
    log.info("server stopped")


app = FastAPI(
    lifespan=lifespan,
    title="Exosphere State Manager",
    description="Exosphere State Manager",
    version="0.0.2-beta",
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


app.include_router(global_router)
app.include_router(router)
