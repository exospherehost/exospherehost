import pytest
import jwt
import datetime
from bson import ObjectId
import json

from starlette.responses import JSONResponse
from bson.errors import InvalidId

from app.auth.controllers import refresh_access_token as refresh_access_token_func
from app.auth.controllers.refresh_access_token import JWT_SECRET_KEY, JWT_ALGORITHM
from app.auth.models import RefreshTokenRequest, TokenResponse
from app.auth.models.token_type_enum import TokenType
from app.user.models import VerificationEnum, StatusEnum

def make_token(user_id, token_type=TokenType.refresh.value, exp_seconds=3600):
    payload = {
        "user_id": str(user_id),
        "token_type": token_type,
        "exp": int(datetime.datetime.utcnow().timestamp()) + exp_seconds
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def _assert_json_error(res, expected_status, expected_detail=None):
    assert isinstance(res, JSONResponse)
    assert res.status_code == expected_status
    body = json.loads(res.body)
    assert body.get("success") is False
    if expected_detail:
        assert expected_detail in body.get("detail", "")

@pytest.mark.asyncio
async def test_refresh_success(monkeypatch):
    class DummyUser:
        id = "507f"
        name = "Alice"
        type = "user"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.ACTIVE.value
        identifier = "alice"

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    class MockProject:
        @staticmethod
        async def get(_):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    token = make_token("507f")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == "507f"
    assert decoded["token_type"] == "access"

@pytest.mark.asyncio
async def test_refresh_invalid_token():
    token = jwt.encode({"token_type": "invalid"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 401, "Invalid token type")

@pytest.mark.asyncio
async def test_refresh_expired_token():
    expired_token = make_token("507f", exp_seconds=-10)
    req = RefreshTokenRequest(refresh_token=expired_token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 401, "Refresh token expired")

@pytest.mark.asyncio
async def test_refresh_user_not_found(monkeypatch):
    class MockUser:
        @staticmethod
        async def get(_):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    token = make_token("507f")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 401)

@pytest.mark.asyncio
async def test_refresh_inactive_user(monkeypatch):
    class DummyUser:
        id = "507f"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.INACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    token = make_token("507f")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 401)

@pytest.mark.asyncio
async def test_refresh_unverified_user(monkeypatch):
    class DummyUser:
        id = "507f"
        verification_status = VerificationEnum.NOT_VERIFIED.value
        status = StatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    token = make_token("507f")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 403)

@pytest.mark.asyncio
async def test_refresh_exception(monkeypatch):
    async def raise_exc(_):
        raise Exception("db fail")

    class MockUser:
        get = staticmethod(raise_exc)

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    token = make_token("507f")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 500)

@pytest.mark.asyncio
async def test_refresh_blocked_user(monkeypatch):
    class DummyUser:
        id = "507f"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.BLOCKED.value

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    token = make_token("507f")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 401)

@pytest.mark.asyncio
async def test_refresh_invalid_project(monkeypatch):
    class DummyUser:
        id = "projuser"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    class MockProject:
        @staticmethod
        async def get(_):
            raise InvalidId("bad id")

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    token = make_token("projuser")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 404)

@pytest.mark.asyncio
async def test_refresh_project_not_found(monkeypatch):
    class DummyUser:
        id = "projuser"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    class MockProject:
        @staticmethod
        async def get(_):
            return None

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    token = make_token("projuser")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 404)

@pytest.mark.asyncio
async def test_refresh_superadmin_privilege(monkeypatch):
    class DummyUser:
        id = "adminuser"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.ACTIVE.value

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    class Ref:
        id = "adminuser"

    class SuperAdmin:
        ref = Ref()

    class MockProject:
        super_admin = SuperAdmin()
        users = []

        @staticmethod
        async def get(_):
            return MockProject()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    token = make_token("adminuser")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    assert isinstance(res, TokenResponse)

@pytest.mark.asyncio
async def test_refresh_user_privilege(monkeypatch):
    class DummyUser:
        id = "userpriv"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.ACTIVE.value

    class ProjectUser:
        permission = type("Permission", (), {"value": "read"})()
        user = type("User", (), {"ref": type("Ref", (), {"id": "userpriv"})()})()

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    class Ref:
        id = "otheruser"

    class MockProject:
        super_admin = type("SuperAdmin", (), {"ref": Ref()})()
        users = [ProjectUser]
        @staticmethod
        async def get(_):
            return MockProject()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    token = make_token("userpriv")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    assert isinstance(res, TokenResponse)

@pytest.mark.asyncio
async def test_refresh_no_privilege(monkeypatch):
    class DummyUser:
        id = "noaccess"
        verification_status = VerificationEnum.VERIFIED.value
        status = StatusEnum.ACTIVE.value

    class ProjectUser:
        permission = type("Permission", (), {"value": "read"})()
        user = type("User", (), {"ref": type("Ref", (), {"id": "otheruser"})()})()

    class MockUser:
        @staticmethod
        async def get(_):
            return DummyUser()

    class Ref:
        id = "someuser"

    class MockProject:
        super_admin = type("SuperAdmin", (), {"ref": Ref()})()
        users = [ProjectUser]
        @staticmethod
        async def get(_):
            return MockProject()

    monkeypatch.setattr("app.auth.controllers.refresh_access_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.refresh_access_token.Project", MockProject)

    token = make_token("noaccess")
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token_func(req, "req-id")
    _assert_json_error(res, 403)

