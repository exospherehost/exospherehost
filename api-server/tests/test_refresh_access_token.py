import pytest
import datetime
import jwt
from bson import ObjectId
from app.auth.controllers.refresh_access_token import refresh_access_token
from app.auth.models.refresh_token_request import RefreshTokenRequest
from app.auth.models.token_type_enum import TokenType
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum
from starlette.responses import JSONResponse

JWT_SECRET_KEY = "testsecret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = 3600

@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    class DummyUser:
        id = ObjectId()
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value

    async def mock_get(_id):
        return DummyUser()

    class MockUser:
        get = staticmethod(mock_get)

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(DummyUser.id),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert res is not None

@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found(monkeypatch):
    class MockUser:
        @staticmethod
        async def get(_id):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_refresh_access_token_unverified_user(monkeypatch):
    class DummyUser:
        id = ObjectId()
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.UNVERIFIED.value
        status = UserStatusEnum.ACTIVE.value

    async def mock_get(_id):
        return DummyUser()

    class MockUser:
        get = staticmethod(mock_get)

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(DummyUser.id),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_refresh_access_token_project_super_admin(monkeypatch):
    class DummyUser:
        id = ObjectId()
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value

    class DummyProject:
        super_admin = type("ref", (), {"ref": type("user", (), {"id": DummyUser.id})})
        users = []

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    class MockProject:
        @staticmethod
        async def get(_id):
            return DummyProject()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    payload = {
        "user_id": str(DummyUser.id),
        "project": str(ObjectId()),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert res is not None

@pytest.mark.asyncio
async def test_refresh_access_token_exception(monkeypatch):
    async def bad_get(_id):
        raise Exception("DB fail")

    class MockUser:
        get = staticmethod(bad_get)

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 500
