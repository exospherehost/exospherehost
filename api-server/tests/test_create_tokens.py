import pytest
import jwt
from starlette.responses import JSONResponse

from app.auth.controllers.create_token import create_token, JWT_SECRET_KEY, JWT_ALGORITHM
from app.auth.models.token_request import TokenRequest
from app.auth.models.token_response import TokenResponse
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum


@pytest.mark.asyncio
async def test_create_token_success(monkeypatch):
    class DummyUser:
        id = "507f1f77bcf86cd799439011"
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        def verify_credential(self, cred):
            return True

    async def mock_find_one(_query):
        return DummyUser()

    class MockUser:
        identifier="identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded["token_type"] == "access"


@pytest.mark.asyncio
async def test_create_token_invalid_user(monkeypatch):
    async def mock_find_one(_query):
        return None

    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="bad", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_token_inactive_user(monkeypatch):
    class DummyUser:
        type="admin"
        name="john"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.INACTIVE.value

        def verify_credential(self, cred):
            return True

    async def mock_find_one(_query):
        return DummyUser()

    class MockUser:
        identifier="req-id"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_token_unverified_user(monkeypatch):
    class DummyUser:
        type="admin"
        name="john"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.NOT_VERIFIED.value
        status = UserStatusEnum.ACTIVE.value

        def verify_credential(self, cred):
            return True

    async def mock_find_one(_query):
        return DummyUser()

    class MockUser:
        identifier="req-id"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_token_exception(monkeypatch):
    async def bad_find_one(_query):
        raise Exception("DB error")

    class MockUser:
        identifier="req-id"
        find_one = staticmethod(bad_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 500
@pytest.mark.asyncio
async def test_create_token_blocked_user(monkeypatch):
    class DummyUser:
        type = "admin"
        name = "john"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.BLOCKED.value
        def verify_credential(self, cred): return True

    async def mock_find_one(_query): return DummyUser()

    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403