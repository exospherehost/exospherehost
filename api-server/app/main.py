"""
main file for exosphere apis
"""
import os
from beanie import init_beanie
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import OAuth2PasswordBearer

# injecting singletons
from .singletons.logs_manager import LogsManager

# injecting middlewares
from .middlewares.unhandled_exceptions_middleware import (
    UnhandledExceptionsMiddleware,
)
from .middlewares.request_id_middleware import RequestIdMiddleware
from .auth.middlewares.get_token_claims import GetTokenClaimsMiddleware

# injecting databases
from .user.models.user_database_model import User
from .project.models.project_database_model import Project

# injecting routers
from .user.routes import router as user_router
from .auth.router import router as auth_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # begaining of the server
    logger = LogsManager().get_logger()
    logger.info("server starting")

    # initializing beanie
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DATABASE_NAME")]
    await init_beanie(db, document_models=[User, Project])
    logger.info("beanie dbs initialized")

    # main logic of the server
    yield

    # end of the server
    logger.info("server shutting down")


app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# this middleware should be the first one
app.add_middleware(GetTokenClaimsMiddleware)

app.add_middleware(RequestIdMiddleware)

app.add_middleware(UnhandledExceptionsMiddleware)



@app.get("/health-check")
def health() -> dict:
    return {"message": "OK"}

# injecting routers
app.include_router(user_router)
app.include_router(auth_router)
