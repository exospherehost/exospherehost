import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    """
    Automatically sets required environment variables for tests
    so that modules depending on them don't raise ValueError.
    """
    os.environ.setdefault("JWT_SECRET_KEY", "test_secret")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("JWT_EXPIRES_IN", "3600")  # 1 hour
