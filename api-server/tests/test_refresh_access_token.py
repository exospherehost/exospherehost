import pytest
import jwt
import datetime
from bson import ObjectId
import json
from starlette.responses import JSONResponse
from bson.errors import InvalidId
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

def _assert_json_error(res, expected_status: int, expected_detail: str | None = None):
    assert isinstance(res, JSONResponse)
    assert res.status_code == expected_status
    body = json.loads(res.body)
    assert body.get("success") is False
    if expected_detail is not None:
        assert expected_detail in body.get("detail", "")

@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    class DummyUser:
        name = "john"
        type = "dummy"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        identifier = "none"

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    class MockProject:
        @staticmethod
        async def get(_id):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.project.models.project_database_model.Project", MockProject)

    token = make_token("507f1f77bcf86cd799439011")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded["token_type"] == "access"

@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token():
    bad_token = jwt.encode({"token_type": "wrong"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=bad_token)
    res = await refresh_access_token(req, "req-id")
    _assert_json_error(res, 401, "Invalid token type")

@pytest.mark.asyncio
async def test_refresh_access_token_expired_token():
    token = make_token("507f1f77bcf86cd799439011", exp_seconds=-10)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    _assert_json_error(res, 401, "Refresh token expired")

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
    _assert_json_error(res, 401)

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
    _assert_json_error(res, 401)

@pytest.mark.asyncio
async def test_refresh_access_token_unverified_user(monkeypatch):
    class DummyUser:
        type = "trial"
        name = "john"
        id = "507f1f77bcf86cd799439011"
        verification_status = VerificationStatusEnum.NOT_VERIFIED.value
        status = UserStatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    token = make_token("507f1f77bcf86cd799439011")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    _assert_json_error(res, 403)

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
    _assert_json_error(res, 500)

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
    _assert_json_error(res, 401)

# ---- PROJECT TESTS ----

@pytest.mark.asyncio
async def test_refresh_token_invalid_project(monkeypatch):
    class DummyUser:
        id = "user123"
        verification_status = "VERIFIED"
        status = "ACTIVE"
    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()
    class MockProject:
        @staticmethod
        async def get(_id):
            raise InvalidId("invalid project")
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.project.models.project_database_model.Project", MockProject)
    token = make_token(DummyUser.id)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    _assert_json_error(res, 404, "Project")

@pytest.mark.asyncio
async def test_refresh_token_project_not_found(monkeypatch):
    class DummyUser:
        id = "user123"
        verification_status = "VERIFIED"
        status = "ACTIVE"
    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()
    class MockProject:
        @staticmethod
        async def get(_id):
            return None
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.project.models.project_database_model.Project", MockProject)
    token = make_token(DummyUser.id)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    _assert_json_error(res, 404, "Project")

@pytest.mark.asyncio
async def test_refresh_token_project_privilege_superadmin(monkeypatch):
    class DummyUser:
        id = "user123"
        verification_status = "VERIFIED"
        status = "ACTIVE"
    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()
    class Ref:
        id = "user123"
    class SuperAdmin:
        ref = Ref()
    class MockProject:
        super_admin = SuperAdmin()
        users = []
        @staticmethod
        async def get(_id):
            return MockProject()
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.project.models.project_database_model.Project", MockProject)
    token = make_token(DummyUser.id)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, TokenResponse)

@pytest.mark.asyncio
async def test_refresh_token_project_privilege_user(monkeypatch):
    class DummyUser:
        id = "user123"
        verification_status = "VERIFIED"
        status = "ACTIVE"
    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()
    class ProjectUser:
        permission = type("Permission", (), {"value": "read"})()
        user = type("User", (), {"ref": type("Ref", (), {"id": "user123"})()})()
    class Ref:
        id = "not_user"
    class SuperAdmin:
        ref = Ref()
    class MockProject:
        super_admin = SuperAdmin()
        users = [ProjectUser]
        @staticmethod
        async def get(_id):
            return MockProject()
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.project.models.project_database_model.Project", MockProject)
    token = make_token(DummyUser.id)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, TokenResponse)

@pytest.mark.asyncio
async def test_refresh_token_project_no_access(monkeypatch):
    class DummyUser:
        id = "user123"
        verification_status = "VERIFIED"
        status = "ACTIVE"
    class MockUser:
        @staticmethod
        async def get(_id):
            return DummyUser()
    class ProjectUser:
        permission = type("Permission", (), {"value": "read"})()
        user = type("User", (), {"ref": type("Ref", (), {"id": "other_user"})()})()
    class Ref:
        id = "not_user"
    class SuperAdmin:
        ref = Ref()
    class MockProject:
        super_admin = SuperAdmin()
        users = [ProjectUser]
        @staticmethod
        async def get(_id):
            return MockProject()
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.project.models.project_database_model.Project", MockProject)
    token = make_token(DummyUser.id)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")
    _assert_json_error(res, 403, "User")
