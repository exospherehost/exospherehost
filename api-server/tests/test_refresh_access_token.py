import os
import pytest
import jwt
from starlette.responses import JSONResponse

from app.auth.controllers.refresh_access_token import refresh_access_token, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRES_IN
from app.auth.controllers.refresh_access_token import RefreshTokenRequest
from app.auth.controllers.refresh_access_token import TokenResponse
from app.auth.controllers.refresh_access_token import TokenType

@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    os.environ["JWT_SECRET_KEY"] = "test_secret"

    class DummyUser:
        id = "123"
        name = "John"
        type = "admin"
        verification_status = "verified"
        status = "active"

    async def mock_user_get(_): return DummyUser()
    async def mock_project_get(_): return None

    monkeypatch.setattr("api_server.refresh_access_token.User.get", mock_user_get)
    monkeypatch.setattr("api_server.refresh_access_token.Project.get", mock_project_get)

    import datetime
    payload = {
        "user_id": "123",
        "token_type": TokenType.refresh.value,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXPIRES_IN)).timestamp())
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=token)
    res = await refresh_access_token(req, "req-id")

    assert isinstance(res, TokenResponse)
    decoded_access = jwt.decode(res.access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded_access["user_id"] == "123"
    assert decoded_access["token_type"] == "access"

@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(monkeypatch):
    bad_token = jwt.encode({"token_type": "wrong"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    req = RefreshTokenRequest(refresh_token=bad_token)
    res = await refresh_access_token(req, "req-id")
    assert isinstance(res, JSONResponse)
    assert res.status_code == 401
