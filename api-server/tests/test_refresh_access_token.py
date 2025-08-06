import pytest
import jwt
from starlette.responses import JSONResponse

from app.auth.controllers.refresh_access_token import (
    refresh_access_token,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRES_IN
)
from app.auth.models.refresh_token_request import RefreshTokenRequest
from app.auth.models.token_response import TokenResponse
from app.auth.models.token_type_enum import TokenType

@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")

    class DummyUser:
        id = "507f1f77bcf86cd799439011"
        name = "John"
        type = "admin"
        verification_status = "verified"
        status = "active"  # must be active to pass

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    class MockProject:
        @staticmethod
        async def get(_id):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    import datetime
    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp())
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded["token_type"] == "access"

@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")

    bad_token = jwt.encode({"token_type": "wrong"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=bad_token)
    res = await refresh_access_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 401
