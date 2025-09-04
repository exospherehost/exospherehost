import pytest
import asyncio
import threading
import time
import uvicorn
from app.main import app


class UvicornTestServer:
    """
    A proper uvicorn server for integration testing with real HTTP endpoints.
    This runs the server in a background thread with proper startup and shutdown.
    """
    
    def __init__(self, app, host="127.0.0.1", port=None):
        self.app = app
        self.host = host
        self.port = port or self._find_free_port()
        self.server = None
        self.thread = None
        self.started = False
    
    def _find_free_port(self):
        """Find a free port to avoid conflicts."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start(self):
        """Start the uvicorn server in a background thread."""
        if self.started:
            return
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        self.server = uvicorn.Server(config)
        
        def run_server():
            """Run the server in the thread."""
            assert self.server is not None
            asyncio.run(self.server.serve())
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # Wait for server to be ready
        self._wait_for_server()
        self.started = True
        print(f"🚀 Server started on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the server gracefully."""
        if not self.started:
            return
        
        print("🛑 Stopping server...")
        if self.server:
            self.server.should_exit = True
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
        
        self.started = False
        print("✅ Server stopped")
    
    def _wait_for_server(self, timeout=30):
        """Wait for the server to accept connections."""
        import socket
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((self.host, self.port))
                    if result == 0:
                        return
            except Exception:
                pass
            time.sleep(0.2)
        
        raise RuntimeError(f"Server failed to start within {timeout} seconds")
    
    @property
    def base_url(self):
        """Get the base URL of the running server."""
        return f"http://{self.host}:{self.port}"


@pytest.fixture(scope="session")
def running_server():
    """
    Session-scoped fixture that provides a fresh server for each test.
    Use this when you need isolation between tests.
    """
    server = UvicornTestServer(app)
    server.start()
    yield server
    server.stop()

