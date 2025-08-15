import pytest
import jwt
from starlette.responses import JSONResponse
from bson.errors import InvalidId

from app.auth.controllers.create_token import create_token, JWT_SECRET_KEY, JWT_ALGORITHM
from app.auth.models.token_request import TokenRequest
from app.auth.models.token_response import TokenResponse
from app.user.models.user_status_enum import UserStatusEnum
from app.user.models.verification_status_enum import VerificationStatusEnum

# Use valid ObjectIds everywhere!
VALID_USER_ID = "507f1f77bcf86cd799439011"
ALT_USER_ID = "507f1f77bcf86cd799439012"
OTHER_USER_ID = "507f1f77bcf86cd799439013"
PROJECT_ID = "507f1f77bcf86cd799439014"
NOT_ME_ID = "507f1f77bcf86cd799439015"
OTHER_PROJECT_ID = "507f1f77bcf86cd799439016"

@pytest.mark.asyncio
async def test_create_token_success(monkeypatch):
    class DummyUser:
        id = VALID_USER_ID
        name = "John"
        type = "admin"
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        def verify_credential(self, cred): return True

    async def mock_find_one(_query): return DummyUser()
    class MockUser:
        identifier="identifier"
        find_one = staticmethod(mock_find_one)

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == VALID_USER_ID
    assert decoded["token_type"] == "access"

@pytest.mark.asyncio
async def test_create_token_invalid_user(monkeypatch):
    async def mock_find_one(_query): return None
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
        id = VALID_USER_ID
        verification_status = VerificationStatusEnum.VERIFIED.value
        status = UserStatusEnum.INACTIVE.value
        def verify_credential(self, cred): return True
    async def mock_find_one(_query): return DummyUser()
    class MockUser:
        identifier="identifier"
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
        id = VALID_USER_ID
        verification_status = VerificationStatusEnum.NOT_VERIFIED.value
        status = UserStatusEnum.ACTIVE.value
        def verify_credential(self, cred): return True
    async def mock_find_one(_query): return DummyUser()
    class MockUser:
        identifier="identifier"
        find_one = staticmethod(mock_find_one)
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_create_token_exception(monkeypatch):
    async def bad_find_one(_query): raise Exception("DB error")
    class MockUser:
        identifier="identifier"
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
        id = VALID_USER_ID
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

@pytest.mark.asyncio
async def test_create_token_invalid_project_id(monkeypatch):
    class DummyUser:
        id = VALID_USER_ID
        name = "John"
        type = "admin"
        verification_status = "VERIFIED"
        status = "ACTIVE"
        def verify_credential(self, _): return True
    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(lambda _query: DummyUser())
    class MockProject:
        @staticmethod
        async def get(_id): raise InvalidId("invalid project")
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project="invalid507f1f77bcf86cd799439077", satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 400
    assert b"Invalid project" in res.body

@pytest.mark.asyncio
async def test_create_token_project_not_found(monkeypatch):
    class DummyUser:
        id = VALID_USER_ID
        name = "John"
        type = "admin"
        verification_status = "VERIFIED"
        status = "ACTIVE"
        def verify_credential(self, _): return True
    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(lambda _query: DummyUser())
    class MockProject:
        @staticmethod
        async def get(_id): return None
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project=PROJECT_ID, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 404
    assert b"Project" in res.body

@pytest.mark.asyncio
async def test_create_token_super_admin_project(monkeypatch):
    class DummyUser:
        id = VALID_USER_ID
        name = "John"
        type = "admin"
        verification_status = "VERIFIED"
        status = "ACTIVE"
        def verify_credential(self, _): return True
    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(lambda _query: DummyUser())
    class MockProject:
        super_admin = type("SuperAdmin", (), {"ref": type("Ref", (), {"id": VALID_USER_ID})()})()
        users = []
        @staticmethod
        async def get(_id): return MockProject()
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project=PROJECT_ID, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, TokenResponse)

@pytest.mark.asyncio
async def test_create_token_user_with_project_permission(monkeypatch):
    class DummyUser:
        id = ALT_USER_ID
        name = "John"
        type = "admin"
        verification_status = "VERIFIED"
        status = "ACTIVE"
        def verify_credential(self, _): return True
    class ProjectUser:
        permission = type("Permission", (), {"value": "read"})()
        user = type("User", (), {"ref": type("Ref", (), {"id": ALT_USER_ID})()})()
    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(lambda _query: DummyUser())
    class MockProject:
        super_admin = type("SuperAdmin", (), {"ref": type("Ref", (), {"id": VALID_USER_ID})()})()
        users = [ProjectUser]
        @staticmethod
        async def get(_id): return MockProject()
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project=PROJECT_ID, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, TokenResponse)

@pytest.mark.asyncio
async def test_create_token_user_without_project_permission(monkeypatch):
    class DummyUser:
        id = OTHER_USER_ID
        name = "John"
        type = "admin"
        verification_status = "VERIFIED"
        status = "ACTIVE"
        def verify_credential(self, _): return True
    class ProjectUser:
        permission = type("Permission", (), {"value": "read"})()
        user = type("User", (), {"ref": type("Ref", (), {"id": NOT_ME_ID})()})()
    class MockUser:
        identifier = "identifier"
        find_one = staticmethod(lambda _query: DummyUser())
    class MockProject:
        super_admin = type("SuperAdmin", (), {"ref": type("Ref", (), {"id": VALID_USER_ID})()})()
        users = [ProjectUser]
        @staticmethod
        async def get(_id): return MockProject()
    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)
    req = TokenRequest(identifier="user", credential="pass", project=PROJECT_ID, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 403
    assert b"User" in res.body
