import os
import pytest
import jwt
from starlette.responses import JSONResponse

from app.auth.controllers.create_token import create_token, JWT_SECRET_KEY, JWT_ALGORITHM
from app.auth.models.token_request import TokenRequest
from app.auth.models.token_response import TokenResponse

@pytest.mark.asyncio
async def test_create_token_success(monkeypatch):
    # Set fake secret key for testing
    os.environ["JWT_SECRET_KEY"] = "test_secret"

    # Dummy user to simulate DB lookup
    class DummyUser:
        id = "123"
        name = "John"
        type = "admin"
        verification_status = "verified"
        status = "active"
        def verify_credential(self, cred):
            return True

    async def mock_find_one(query):
        return DummyUser()

    async def mock_project_get(_):
        return None  # no project check for this test

    # Patch User.find_one and Project.get
    monkeypatch.setattr("app.auth.controllers.create_token.User.find_one", mock_find_one)
    monkeypatch.setattr("app.auth.controllers.create_token.Project.get", mock_project_get)

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded_access = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded_access["user_id"] == "123"
    assert decoded_access["token_type"] == "access"

@pytest.mark.asyncio
async def test_create_token_invalid_user(monkeypatch):
    # Patch User.find_one to return None (user not found)
    async def mock_find_one(query):
        return None

    monkeypatch.setattr("app.auth.controllers.create_token.User.find_one", mock_find_one)

    req = TokenRequest(identifier="bad", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 404
