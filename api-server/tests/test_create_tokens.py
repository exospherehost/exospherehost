import os
import jwt
import types
import pytest
import importlib
from starlette.responses import JSONResponse
from bson.errors import InvalidId

from app.auth.controllers.create_token import create_token, JWT_ALGORITHM
from app.auth.models.token_request import TokenRequest
from app.auth.models.token_response import TokenResponse
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum


@pytest.fixture
def dummy_user_cls():
    class DummyUser:
        id = "507f1f77bcf86cd799439011"
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        def __init__(self, **overrides):
            for k, v in overrides.items():
                setattr(self, k, v)
        def verify_credential(self, cred):
            return True
    return DummyUser


def patch_user_find_one(monkeypatch, user_obj):
    async def mock_find_one(_):
        return user_obj
    MockUser = types.SimpleNamespace(identifier="identifier", find_one=staticmethod(mock_find_one))
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)


@pytest.mark.asyncio
async def test_create_token_success(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls()
    patch_user_find_one(monkeypatch, user)
    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, os.getenv("JWT_SECRET_KEY"), algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded["token_type"] == "access"
    decoded_refresh = jwt.decode(res.refresh_token, os.getenv("JWT_SECRET_KEY"), algorithms=[JWT_ALGORITHM])
    assert decoded_refresh["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded_refresh["token_type"] == "refresh"


@pytest.mark.asyncio
async def test_create_token_invalid_user(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    async def mock_find_one(_):
        return None
    MockUser = types.SimpleNamespace(identifier="identifier", find_one=staticmethod(mock_find_one))
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    req = TokenRequest(identifier="bad", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_token_invalid_credential(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls()
    user.verify_credential = lambda cred: False  # override method for this instance
    patch_user_find_one(monkeypatch, user)
    req = TokenRequest(identifier="user", credential="wrong", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_value",
    [UserStatusEnum.INACTIVE.value, UserStatusEnum.BLOCKED.value],
)
async def test_create_token_inactive_blocked_user(monkeypatch, dummy_user_cls, status_value):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls(status=status_value)
    patch_user_find_one(monkeypatch, user)
    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403
    assert "inactive or blocked" in res.body.decode().lower()


@pytest.mark.asyncio
async def test_create_token_unverified_user(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls(verification_status=VerificationStatusEnum.NOT_VERIFIED.value)
    patch_user_find_one(monkeypatch, user)
    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403
    assert "not verified" in res.body.decode().lower()


@pytest.mark.asyncio
def test_create_token_missing_jwt_secret(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    import app.auth.controllers.create_token as create_token_module
    with pytest.raises(RuntimeError):
        importlib.reload(create_token_module)


@pytest.mark.asyncio
async def test_create_token_invalid_project_id(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls()
    patch_user_find_one(monkeypatch, user)
    class MockProject:
        @staticmethod
        async def get(_id):
            raise InvalidId("bad id")
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project="badid", satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 400
    assert "invalid project id" in res.body.decode().lower()


@pytest.mark.asyncio
async def test_create_token_project_load_exception(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls()
    patch_user_find_one(monkeypatch, user)
    class MockProject:
        @staticmethod
        async def get(_id):
            raise Exception("db error")
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project="507f1f77bcf86cd799439012", satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 500
    assert "internal server error" in res.body.decode().lower()


@pytest.mark.asyncio
async def test_create_token_project_not_found(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls()
    patch_user_find_one(monkeypatch, user)
    class MockProject:
        @staticmethod
        async def get(_id):
            return None
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project="507f1f77bcf86cd799439012", satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 404
    assert "project not found" in res.body.decode().lower()


@pytest.mark.asyncio
async def test_create_token_project_no_privilege(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    user = dummy_user_cls()
    patch_user_find_one(monkeypatch, user)
    class DummyProject:
        super_admin = type("SuperAdmin", (), {"ref": type("Ref", (), {"id": "otherid"})})()
        users = []
    class MockProject:
        @staticmethod
        async def get(_id):
            return DummyProject()
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project="507f1f77bcf86cd799439012", satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403
    assert "does not have access" in res.body.decode().lower()


@pytest.mark.asyncio
async def test_create_token_unhandled_exception(monkeypatch, dummy_user_cls):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    async def mock_find_one(_):
        raise Exception("unexpected error")
    MockUser = types.SimpleNamespace(identifier="identifier", find_one=staticmethod(mock_find_one))
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 500
    assert "internal server error" in res.body.decode().lower()
