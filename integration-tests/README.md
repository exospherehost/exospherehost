# Integration Testing with Uvicorn Server

This directory contains examples of how to properly run and stop uvicorn servers for integration testing. Unlike the problematic approach of using `uvicorn.run()` (which blocks forever), these examples show you how to create real HTTP endpoints that you can send requests to.

## 🚨 The Problem with `uvicorn.run()`

The original code had this issue:

```python
@pytest.mark.asyncio
async def test_basic():
    uvicorn.run(app, host="127.0.0.1", port=8000)  # ❌ This blocks forever!
    async with ClientSession() as session:  # ❌ This never executes
        # ... test code that never runs
```

**Problem**: `uvicorn.run()` is a blocking call that never returns, so your test code after it never executes.

## ✅ Proper Solutions

### 1. UvicornTestServer Class (Recommended)

The `UvicornTestServer` class in `test_basic.py` provides a clean way to start and stop uvicorn servers:

```python
from test_basic import UvicornTestServer

# Create and start server
server = UvicornTestServer(app, host="127.0.0.1", port=8000)
server.start()

# Make HTTP requests
async with ClientSession() as session:
    async with session.get(f"{server.base_url}/health") as response:
        assert response.status == 200

# Stop server
server.stop()
```

**Features:**
- ✅ Automatic port detection (avoids conflicts)
- ✅ Proper startup/shutdown lifecycle
- ✅ Thread-based server execution
- ✅ Waits for server to be ready
- ✅ Graceful cleanup

### 2. Pytest Fixtures

Use pytest fixtures for automatic server management:

```python
@pytest.fixture(scope="session")
def running_server():
    """Server shared across all tests in the session."""
    server = UvicornTestServer(app)
    server.start()
    yield server
    server.stop()

@pytest.fixture(scope="function")
def fresh_server():
    """Fresh server for each test."""
    server = UvicornTestServer(app)
    server.start()
    yield server
    server.stop()
```

### 3. Manual Server Management

For full control over server lifecycle:

```python
@pytest.mark.asyncio
async def test_manual_server():
    server = UvicornTestServer(app)
    
    try:
        server.start()
        # Your test code here
        async with ClientSession() as session:
            async with session.get(f"{server.base_url}/health") as response:
                assert response.status == 200
    finally:
        server.stop()  # Always cleanup
```

## 🏃‍♂️ Running the Examples

### Install Dependencies

```bash
cd integration-tests
uv sync
```

### Run Tests

```bash
# Run all tests
uv run python -m pytest test_basic.py -v

# Run specific test
uv run python -m pytest test_basic.py::test_basic_with_session_server -v -s

# Run with output
uv run python -m pytest test_basic.py -v -s
```

### Run Demo Server

```bash
# Start a server you can send requests to
uv run python demo_server.py
```

Then in another terminal:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/test
```

## 📁 File Overview

- **`test_basic.py`** - Main test file with UvicornTestServer class and examples
- **`test_server_examples.py`** - Comprehensive examples of different testing approaches
- **`demo_server.py`** - Simple script to run a server manually
- **`pyproject.toml`** - Project dependencies

## 🎯 When to Use Each Approach

### Session-Scoped Server (`running_server` fixture)
- ✅ Fast test execution (server starts once)
- ✅ Good for multiple tests that don't interfere
- ❌ Tests share state
- **Use for**: Most integration tests

### Function-Scoped Server (`fresh_server` fixture)  
- ✅ Complete isolation between tests
- ✅ Clean state for each test
- ❌ Slower (starts server for each test)
- **Use for**: Tests that modify server state

### Manual Server Management
- ✅ Full control over lifecycle
- ✅ Can test server startup/shutdown
- ❌ More verbose
- **Use for**: Complex scenarios, debugging

### Demo Server Script
- ✅ Perfect for development and debugging
- ✅ Can send real HTTP requests
- ✅ Easy to test endpoints manually
- **Use for**: Development, manual testing

## 🔧 Key Features of UvicornTestServer

1. **Automatic Port Detection**: Finds free ports to avoid conflicts
2. **Proper Lifecycle**: Clean startup and shutdown
3. **Thread Safety**: Runs server in background thread
4. **Health Checking**: Waits for server to be ready
5. **Graceful Shutdown**: Proper cleanup on exit
6. **Error Handling**: Robust error handling and timeouts

## 🚀 Making HTTP Requests

Once you have a running server, you can make requests using:

### With aiohttp (async)
```python
async with ClientSession() as session:
    async with session.get(f"{server.base_url}/health") as response:
        data = await response.json()
        assert data["message"] == "OK"
```

### With httpx (async)
```python
async with httpx.AsyncClient() as client:
    response = await client.get(f"{server.base_url}/health")
    assert response.status_code == 200
```

### With curl (command line)
```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/data -H "Content-Type: application/json" -d '{"key": "value"}'
```

### With requests (sync)
```python
import requests
response = requests.get(f"{server.base_url}/health")
assert response.status_code == 200
```

## 🎉 Success!

Now you have a proper way to run uvicorn servers for integration testing that:
- ✅ Actually starts and stops properly
- ✅ Provides real HTTP endpoints
- ✅ Handles cleanup automatically
- ✅ Avoids port conflicts
- ✅ Works reliably in CI/CD

No more blocking `uvicorn.run()` calls or tests that never execute! 