"""
main file for exosphere state manager
"""
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from pymongo.database import Database
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

# Use LogsManager for consistent structured logging across the app
logger = LogsManager().get_logger()


async def ensure_ttl_indexes(
    db: Database,
    ttl_days: int = 30,
    collections: Optional[List[str]] = None,
    timestamp_field: str = "created_at"
):
    """
    Ensure TTL indexes exist on the specified collections.
    
    Creates a TTL (Time To Live) index that automatically deletes documents after
    they reach a certain age based on a timestamp field. If an index already exists
    with a different expireAfterSeconds value, it will be updated using collMod.

    Args:
        db: async pymongo Database instance (from AsyncMongoClient)
        ttl_days: number of days after which documents should expire (default: 30)
        collections: list of collection names to apply TTL to (defaults to ['runs'])
        timestamp_field: name of the timestamp field to create TTL index on (default: 'created_at')
    """
    if collections is None:
        collections = ["runs"]

    ttl_seconds = int(ttl_days) * 24 * 3600
    index_name = f"ttl_{timestamp_field}_index"

    for coll_name in collections:
        try:
            coll = db.get_collection(coll_name)
            
            # Check for existing indexes
            existing_indexes = await coll.index_information()
            
            if index_name in existing_indexes:
                # Index exists, check if expireAfterSeconds differs
                existing_ttl = existing_indexes[index_name].get("expireAfterSeconds")
                
                if existing_ttl is not None and existing_ttl != ttl_seconds:
                    # TTL value differs, update using collMod
                    logger.warning(
                        "TTL index on collection '%s' exists with different expireAfterSeconds (current=%d, desired=%d). Updating...",
                        coll_name,
                        existing_ttl,
                        ttl_seconds
                    )
                    
                    try:
                        # Use collMod to update the expireAfterSeconds value
                        await db.command({
                            "collMod": coll_name,
                            "index": {
                                "name": index_name,
                                "expireAfterSeconds": ttl_seconds
                            }
                        })
                        
                        logger.info(
                            "Successfully updated TTL index on collection '%s' from %d to %d seconds",
                            coll_name,
                            existing_ttl,
                            ttl_seconds
                        )
                    except Exception as mod_error:
                        logger.error(
                            "Failed to update TTL index on collection '%s': %s. Will attempt to recreate.",
                            coll_name,
                            mod_error,
                            exc_info=True
                        )
                        
                        # If collMod fails, drop and recreate
                        await coll.drop_index(index_name)
                        logger.info("Dropped existing TTL index '%s' on collection '%s'", index_name, coll_name)
                        
                        await coll.create_index(
                            [(timestamp_field, 1)],
                            expireAfterSeconds=ttl_seconds,
                            name=index_name
                        )
                        
                        logger.info(
                            "Recreated TTL index on collection '%s' with expireAfterSeconds=%d",
                            coll_name,
                            ttl_seconds
                        )
                else:
                    # Index exists with correct TTL value
                    logger.info(
                        "TTL index on collection '%s' already exists with correct expireAfterSeconds=%d",
                        coll_name,
                        ttl_seconds
                    )
            else:
                # Index doesn't exist, create it
                await coll.create_index(
                    [(timestamp_field, 1)],
                    expireAfterSeconds=ttl_seconds,
                    name=index_name
                )
                
                logger.info(
                    "Successfully created TTL index on collection '%s' with field '%s' (expireAfterSeconds=%d, ttl_days=%d)",
                    coll_name,
                    timestamp_field,
                    ttl_seconds,
                    ttl_days
                )
                
        except Exception as e:
            # Log error but don't crash the server
            logger.error(
                "Failed to ensure TTL index on collection '%s' with field '%s': %s",
                coll_name,
                timestamp_field,
                e,
                exc_info=True
            )

    logger.info("TTL index setup completed for collections: %s", collections)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # beginning of the server
    logger.info("server starting")

    # Get settings
    settings = get_settings()

    # initializing beanie (and Mongo client)
    client = AsyncMongoClient(settings.mongo_uri)
    db = client[settings.mongo_database_name]

    # Initialize beanie models (this registers document models / collections)
    await init_beanie(db, document_models=DOCUMENT_MODELS)
    logger.info("beanie dbs initialized")

    # --- ENSURE TTL INDEXES (conservative, before init_tasks) ---
    # Start with 'runs' only to be safe. Add other collections once you confirm.
    # Uses 'created_at' field by default (can be customized via timestamp_field parameter)
    logger.info("Starting TTL index creation...")
    try:
        await ensure_ttl_indexes(db, ttl_days=settings.ttl_days, collections=["runs"])
        logger.info("TTL index creation completed successfully")
    except Exception as e:
        # By default we log and continue. If you want fail-fast, replace with `raise`.
        logger.exception("Error while ensuring TTL indexes: %s", e)

    # performing init tasks
    logger.info("Starting init tasks...")
    await init_tasks()
    logger.info("init tasks completed")

    # initialize secret
    if not settings.state_manager_secret:
        # this is critical — fail immediately
        raise ValueError("STATE_MANAGER_SECRET is not set")
    logger.info("secret initialized")

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
    logger.info("server stopped")


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
