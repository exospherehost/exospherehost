import uuid
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

# Import your middleware classes here
from app.middlewares.request_id_middleware import RequestIdMiddleware
from app.middlewares.unhandled_exceptions_middleware import UnhandledExceptionsMiddleware

# --- Dummy endpoint that returns OK JSON ---
async def ok_endpoint(request: Request):
    # When called, respond with JSON {"status": "ok"}
    """
    Handle a request and return a JSON response indicating success.
    
    Returns:
        JSONResponse: A response with JSON body {"status": "ok"}.
    """
    return JSONResponse({"status": "ok"})

# --- Dummy endpoint that raises an exception ---
async def fail_endpoint(request: Request):
    # When called, raise a ValueError to simulate an error
    """
    Simulates an endpoint that always raises a ValueError to test error handling middleware.
    """
    raise ValueError("oops")

@pytest.fixture
def client():
    """
    Pytest fixture that provides a TestClient for a FastAPI app configured with custom middlewares and test endpoints.
    
    Returns:
        TestClient: A client for simulating HTTP requests to the app with middlewares applied.
    """
    app = FastAPI()

    # Add middlewares. Order matters! Exceptions should be handled outermost.
    app.add_middleware(UnhandledExceptionsMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Add routes tied to the dummy endpoints above
    app.add_api_route("/ok", ok_endpoint, methods=["GET"])
    app.add_api_route("/fail", fail_endpoint, methods=["GET"])

    # Return a test client wrapping the ASGI app for test requests
    return TestClient(app)

def test_request_id_auto_generated(client):
    """
    Test that when no 'x-exosphere-request-id' header is sent, the RequestIdMiddleware
    automatically generates a valid UUID and returns it in the response headers.
    """
    resp = client.get("/ok")  # Make GET request without headers
    assert resp.status_code == 200  # Should return HTTP 200 OK

    rid = resp.headers["x-exosphere-request-id"]  # Get the request ID from headers
    uuid.UUID(rid)  # Validate that it is a valid UUID (will raise an exception if not)

    assert resp.json() == {"status": "ok"}  # Response body should be unchanged

def test_request_id_echoed_when_valid(client):
    """
    Test that when a valid UUID is provided in header, middleware preserves (echoes) it.
    """
    provided = str(uuid.uuid4())  # Generate a valid UUID string
    resp = client.get("/ok", headers={"x-exosphere-request-id": provided})  # Send header

    assert resp.headers["x-exosphere-request-id"] == provided  # Header echoed exactly

def test_request_id_replaced_when_invalid(client):
    """
    Test that when an invalid request ID is sent, middleware replaces it with a valid UUID.
    """
    resp = client.get("/ok", headers={"x-exosphere-request-id": "invalid-id"})  # Send bad header

    new_rid = resp.headers["x-exosphere-request-id"]
    assert new_rid != "invalid-id"  # Confirm the invalid ID was replaced
    uuid.UUID(new_rid)  # Confirm replacement is a valid UUID

def test_unhandled_exception_caught(client):
    """
    Test that any unhandled exception during request processing is caught by the middleware,
    returning a JSON error with HTTP status 500, and still providing a request ID header.
    """
    resp = client.get("/fail")  # This route raises an exception

    assert resp.status_code == 500  # Middleware converts error to HTTP 500 response

    body = resp.json()
    assert "error" in body or "detail" in body  # Error info present in JSON response body

    assert "x-exosphere-request-id" in resp.headers  # Request ID header is still present
