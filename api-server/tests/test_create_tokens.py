import pytest
from bson import ObjectId
from app.auth.controllers.create_token import create_token
from app.auth.models.token_request import TokenRequest
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum
from starlette.responses import JSONResponse

@pytest.mark.asyncio
async def test_create_token_success(monkeypatch):
    class DummyUser:
        id = ObjectId("507f1f77bcf86cd799439011")
        identifier = "user"
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value

        def verify_credential(self, cred):
            return True

    async def mock_find_one(_query):
        return DummyUser()

    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse) or res.access_token

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
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_create_token_inactive_user(monkeypatch):
    class DummyUser:
        id = ObjectId()
        identifier = "user"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.INACTIVE.value

        def verify_credential(self, cred):
            return True

    async def mock_find_one(_query):
        return DummyUser()

    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_create_token_unverified_user(monkeypatch):
    class DummyUser:
        id = ObjectId()
        identifier = "user"
        verification_status = VerificationStatusEnum.UNVERIFIED.value
        status = UserStatusEnum.ACTIVE.value

        def verify_credential(self, cred):
            return True

    async def mock_find_one(_query):
        return DummyUser()

    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_create_token_exception(monkeypatch):
    async def mock_find_one(_query):
        raise Exception("DB error")

    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 500