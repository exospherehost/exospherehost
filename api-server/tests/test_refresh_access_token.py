import pytest
import jwt
import datetime
from bson import ObjectId
import json
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
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum


def make_token(user_id, token_type=TokenType.refresh.value, exp_seconds=JWT_EXPIRES_IN):
    payload = {
        "user_id": str(user_id),
        "token_type": token_type,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=exp_seconds)).timestamp())
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    class DummyUser:
        name="john"
        type="dummy"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        identifier="none"

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

    token = make_token("507f1f77bcf86cd799439011")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user-id"]== "507f1f77bcf86cd799439011"
    assert decoded["token_type"] == "access"


@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token():
    bad_token = jwt.encode({"token_type": "wrong"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=bad_token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_access_token_expired_token():
    token = make_token("507f1f77bcf86cd799439011", exp_seconds=-10)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401
    # verify the error payload
    assert json.loads(res.body) == {"detail": "Refresh token expired"}


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found(monkeypatch):
    class MockUser:
        @staticmethod
        async def get(_id):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    token = make_token(ObjectId())
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_access_token_inactive_user(monkeypatch):
    class DummyUser:
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.INACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    token = make_token("507f1f77bcf86cd799439011")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_access_token_unverified_user(monkeypatch):
    class DummyUser:
        type="trial"
        name="john"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.NOT_VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        identifier = "none"
    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    token = make_token("507f1f77bcf86cd799439011")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_refresh_access_token_exception(monkeypatch):
    async def bad_get(_id):
        raise Exception("DB fail")

    class MockUser:
        get = staticmethod(bad_get)

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    token = make_token(ObjectId())
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 500

@pytest.mark.asyncio
async def test_refresh_access_token_blocked_user(monkeypatch):
    class DummyUser:
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.BLOCKED.value

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    token = make_token("507f1f77bcf86cd799439011")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401    
