import pytest
import jwt
from starlette.responses import JSONResponse

from app.auth.controllers.create_token import create_token, JWT_SECRET_KEY, JWT_ALGORITHM
from app.auth.models.token_request import TokenRequest
from app.auth.models.token_response import TokenResponse

@pytest.mark.asyncio
async def test_create_token_success(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")

    class DummyUser:
        id = "507f1f77bcf86cd799439011"
        name = "John"
        type = "admin"
        verification_status = "verified"
        status = "active"
        def verify_credential(self, cred):
            return True

    # Mock User model with identifier attribute and find_one method
    class MockUser:
        identifier = "identifier"
        @staticmethod
        async def find_one(_query):
            return DummyUser()

    # Mock Project model
    class MockProject:
        @staticmethod
        async def get(_id):
            return None

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)
    monkeypatch.setattr("app.auth.controllers.create_token.Project", MockProject)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded["token_type"] == "access"

@pytest.mark.asyncio
async def test_create_token_invalid_user(monkeypatch):
    class MockUser:
        identifier = "identifier"
        @staticmethod
        async def find_one(_query):
            return None

    monkeypatch.setattr("app.auth.controllers.create_token.User", MockUser)

    req = TokenRequest(identifier="bad", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 404
