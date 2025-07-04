"""
main file for exosphere apis
"""
import os
from beanie import init_beanie
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi_jwt_auth import AuthJWT
from motor.motor_asyncio import AsyncIOMotorClient

# injecting singletons
from .singletons.logs_manager import LogsManager

# injecting middlewares
from .middlewares.unhandled_exceptions_middleware import (
    UnhandledExceptionsMiddleware,
)
from .middlewares.request_id_middleware import RequestIdMiddleware

# injecting auth user dependencies
from .auth.models.auth_user_database import AuthUser
from .auth.models.revoked_token_database import RevokedToken
from .auth.routes import router as auth_router
from .auth.settings import AuthJWTSettings

load_dotenv()


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    return (
        await RevokedToken.find_one(RevokedToken.jti == decrypted_token["jti"])
        is not None
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # begaining of the server
    logger = LogsManager().get_logger()
    logger.info("server starting")

    # initializing beanie
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client["exosphere-apis"]
    await init_beanie(db, document_models=[AuthUser, RevokedToken])
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


# injecting routes
app.include_router(auth_router)
