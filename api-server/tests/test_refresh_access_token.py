import pytest
import datetime
import jwt
from bson import ObjectId
from starlette.responses import JSONResponse
from app.auth.controllers.refresh_access_token import refresh_access_token
from app.auth.models.refresh_token_request import RefreshTokenRequest
from app.auth.models.token_response import TokenResponse
from app.auth.models.token_type_enum import TokenType
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum

JWT_SECRET_KEY = "testsecret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN = 3600


def assert_json_response(res, expected_status):
    if isinstance(res, JSONResponse):
        assert res.status_code == expected_status
    elif isinstance(res, TokenResponse):
        raise AssertionError(f"Expected JSONResponse but got TokenResponse: {res.json()}")
    else:
        raise AssertionError(f"Unexpected return type: {type(res)}")


@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    class DummyUser:
        id = ObjectId()
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(DummyUser.id),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, TokenResponse)


@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token():
    req = RefreshTokenRequest(refresh_token="invalid.token.here")
    res = await refresh_access_token(req, "req-id")
    assert_json_response(res, 401)


@pytest.mark.asyncio
async def test_refresh_access_token_expired_token():
    payload = {
        "user_id": str(ObjectId()),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() - datetime.timedelta(seconds=10)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert_json_response(res, 401)


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found(monkeypatch):
    class MockUser:
        @staticmethod
        async def get(_id):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(ObjectId()),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert_json_response(res, 401)  # matches actual code behavior


@pytest.mark.asyncio
async def test_refresh_access_token_inactive_user(monkeypatch):
    class DummyUser:
        id = ObjectId()
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.INACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(DummyUser.id),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert_json_response(res, 403)


@pytest.mark.asyncio
async def test_refresh_access_token_unverified_user(monkeypatch):
    class DummyUser:
        id = ObjectId()
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.UNVERIFIED.value
        status = UserStatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(DummyUser.id),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert_json_response(res, 403)


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
    assert isinstance(res, TokenResponse)


@pytest.mark.asyncio
async def test_refresh_access_token_exception(monkeypatch):
    async def bad_get(_id):
        raise Exception("DB fail")

    class MockUser:
        get = staticmethod(bad_get)

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)

    payload = {
        "user_id": str(ObjectId()),
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert_json_response(res, 500)
