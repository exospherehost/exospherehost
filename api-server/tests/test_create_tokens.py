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

    async def mock_find_one(_query):
        return DummyUser()

    async def mock_project_get(_id):
        return None

    # Patch controller dependencies directly
    monkeypatch.setattr("app.auth.controllers.create_token.User", type("User", (), {"find_one": staticmethod(mock_find_one)}))
    monkeypatch.setattr("app.auth.controllers.create_token.Project", type("Project", (), {"get": staticmethod(mock_project_get)}))

    req = TokenRequest(identifier="user", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded_access = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded_access["user_id"] == "507f1f77bcf86cd799439011"
    assert decoded_access["token_type"] == "access"

@pytest.mark.asyncio
async def test_create_token_invalid_user(monkeypatch):
    async def mock_find_one(_query):
        return None

    # Patch controller dependencies to return no user
    monkeypatch.setattr("app.auth.controllers.create_token.User", type("User", (), {"find_one": staticmethod(mock_find_one)}))

    req = TokenRequest(identifier="bad", credential="pass", project=None, satellites=None)
    res = await create_token(req, "req-id")

    assert isinstance(res, JSONResponse)
    assert res.status_code == 404
