# ExosphereHost Python SDK

[![PyPI version](https://badge.fury.io/py/exospherehost.svg)](https://badge.fury.io/py/exospherehost)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for [ExosphereHost](https://exosphere.host) - an open-source infrastructure layer for background AI workflows and agents. This SDK enables you to create distributed, stateful applications using a node-based architecture.

## Overview

ExosphereHost provides a robust, affordable, and effortless infrastructure for building scalable AI workflows and agents. The Python SDK allows you to:

- Create distributed workflows using a simple node-based architecture.
- Build stateful applications that can scale across multiple compute resources.
- Execute complex AI workflows with automatic state management.
- Integrate with the ExosphereHost platform for optimized performance.

## Installation

```bash
pip install exospherehost
```

## Quick Start

> Important: In v1, all fields in `Inputs`, `Outputs`, and `Secrets` must be strings. If you need to pass complex data (e.g., JSON), serialize the data to a string first, then parse that string within your node.

### Basic Node Creation

Create a simple node that processes data:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class SampleNode(BaseNode):
    class Inputs(BaseModel):
        name: str
        data: str  # v1: strings only

    class Outputs(BaseModel):
        message: str
        processed_data: str  # v1: strings only

    async def execute(self) -> Outputs:
        print(f"Processing data for: {self.inputs.name}")
        # Your processing logic here; serialize complex data to strings (e.g., JSON)
        processed_data = f"completed:{self.inputs.data}"
        return self.Outputs(
            message="success",
            processed_data=processed_data
        )

# Initialize the runtime
Runtime(
    namespace="MyProject",
    name="DataProcessor",
    nodes=[SampleNode]
).start()
```

## Environment Configuration

The SDK requires the following environment variables for authentication with ExosphereHost:

```bash
export EXOSPHERE_STATE_MANAGER_URI="your-state-manager-uri"
export EXOSPHERE_API_KEY="your-api-key"
```

## Key Features

- **Distributed Execution**: Run nodes across multiple compute resources
- **State Management**: Automatic state persistence and recovery
- **Type Safety**: Full Pydantic integration for input/output validation
- **String-only data model (v1)**: All `Inputs`, `Outputs`, and `Secrets` fields are strings. Serialize non-string data (e.g., JSON) as needed.
- **Async Support**: Native async/await support for high-performance operations
- **Error Handling**: Built-in retry mechanisms and error recovery
- **Scalability**: Designed for high-volume batch processing and workflows
- **Graph Store (beta)**: Strings-only key-value store with per-run scope for sharing data across nodes (not durable across separate runs or clusters)

## Architecture

The SDK is built around two core concepts:

### Runtime

The `Runtime` class manages the execution environment and coordinates with the ExosphereHost state manager. It handles:

- Node lifecycle management
- State coordination
- Error handling and recovery
- Resource allocation

### Nodes
Nodes are the building blocks of your workflows. Each node:
- Defines input/output schemas using Pydantic models
- Implements an `execute` method for processing logic
- Can be connected to other nodes to form workflows
- Automatically handles state persistence

## Advanced Usage

### Custom Node Configuration

```python
class ConfigurableNode(BaseNode):
    class Inputs(BaseModel):
        text: str
        max_length: str = "100"  # v1: strings only

    class Outputs(BaseModel):
        result: str
        length: str  # v1: strings only

    async def execute(self) -> Outputs:
        max_length = int(self.inputs.max_length)
        result = self.inputs.text[:max_length]
        return self.Outputs(result=result, length=str(len(result)))
```

### Error Handling

```python
class RobustNode(BaseNode):
    class Inputs(BaseModel):
        data: str

    class Outputs(BaseModel):
        success: str
        result: str

    async def execute(self) -> Outputs:
        raise Exception("This is a test error")
```
Error handling is automatically handled by the runtime and the state manager.

### Working with Secrets

Secrets allow you to securely manage sensitive configuration data like API keys, database credentials, and authentication tokens. Here's how to use secrets in your nodes:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel
import json

class APINode(BaseNode):
    class Inputs(BaseModel):
        user_id: str
        query: str

    class Outputs(BaseModel):
        response: str  # v1: strings only
        status: str

    class Secrets(BaseModel):
        api_key: str
        api_endpoint: str
        database_url: str

    async def execute(self) -> Outputs:
        # Access secrets via self.secrets
        headers = {"Authorization": f"Bearer {self.secrets.api_key}"}
        
        # Use secrets for API calls
        import httpx
        async with httpx.AsyncClient() as client:
            http_response = await client.post(
                f"{self.secrets.api_endpoint}/process",
                headers=headers,
                json={"user_id": self.inputs.user_id, "query": self.inputs.query}
            )
        
        # Serialize body: prefer JSON if valid; fallback to text or empty string
        response_text = http_response.text or ""
        if response_text:
            try:
                response_str = json.dumps(http_response.json())
            except Exception:
                response_str = response_text
        else:
            response_str = ""

        return self.Outputs(
            response=response_str,
            status="success"
        )
```

**Key points about secrets:**

- **Security**: Secrets are stored securely by the ExosphereHost Runtime and are never exposed in logs or error messages
- **Validation**: The `Secrets` class uses Pydantic for automatic validation of secret values
- **String-only (v1)**: All `Secrets` fields must be strings.
- **Access**: Secrets are available via `self.secrets` during node execution
- **Types**: Common secret types include API keys, database credentials, encryption keys, and authentication tokens
- **Injection**: Secrets are injected by the Runtime at execution time, so you don't need to handle them manually

## State Management

The SDK provides a `StateManager` class for programmatically triggering graph executions and managing workflow states. This is useful for integrating ExosphereHost workflows into existing applications or for building custom orchestration logic.

### StateManager Class

The `StateManager` class allows you to trigger graph executions with custom trigger states. It handles authentication and communication with the ExosphereHost state manager service.

#### Initialization

```python
from exospherehost import StateManager

# Initialize with explicit configuration
state_manager = StateManager(
    namespace="MyProject",
    state_manager_uri="https://your-state-manager.exosphere.host",
    key="your-api-key",
    state_manager_version="v0"
)

# Or initialize with environment variables
state_manager = StateManager(namespace="MyProject")
```

**Parameters:**
- `namespace` (str): The namespace for your project
- `state_manager_uri` (str, optional): The URI of the state manager service. If not provided, reads from `EXOSPHERE_STATE_MANAGER_URI` environment variable
- `key` (str, optional): Your API key. If not provided, reads from `EXOSPHERE_API_KEY` environment variable
- `state_manager_version` (str): The API version to use (default: "v0")

#### Triggering Graph Execution

```python
from exospherehost import StateManager, TriggerState

# Create a single trigger state
trigger_state = TriggerState(
    identifier="user-login",
    inputs={
        "user_id": "12345",
        "session_token": "abc123def456",
        "timestamp": "2024-01-15T10:30:00Z"
    }
)

# Trigger the graph (beta store support)
result = await state_manager.trigger(
    "my-graph",
    inputs={
        "user_id": "12345",
        "session_token": "abc123def456"
    },
    store={
        "cursor": "0"  # persisted across nodes (beta)
    }
)
```

**Parameters:**

- `graph_name` (str): Name of the graph to execute
- `inputs` (dict[str, str] | None): Key/value inputs for the first node (strings only)
- `store` (dict[str, str] | None): Graph-level key/value store (beta) persisted across nodes

**Returns:**

- `dict`: JSON payload from the state manager

**Raises:**

- `Exception`: If the HTTP request fails