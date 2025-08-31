# Getting Started

## Installation

```bash
uv add exospherehost
```

## Environment Setup

Set up your environment variables for authentication:
=== ".env File"

    ```bash
    EXOSPHERE_STATE_MANAGER_URI=your-state-manager-uri
    EXOSPHERE_API_KEY=your-api-key
    ```
=== "Environment Variables"

    ```bash
    export EXOSPHERE_STATE_MANAGER_URI="your-state-manager-uri"
    export EXOSPHERE_API_KEY="your-api-key"
    ```

Refer: [Getting State Manager URI](./exosphere/state-manager-setup.md)

## Overview

Exosphere is built around three core concepts:

### 1. Nodes

Nodes are the building blocks of your workflows. Each node:

- Defines input/output schemas using Pydantic models
- Implements an `execute` method for processing logic
- Can be connected to other nodes to form **workflows**
- Automatically handles state persistence

### 2. Runtime

The `Runtime` class manages the execution environment and coordinates with the ExosphereHost state manager. It handles:

- Node lifecycle management
- State coordination
- Error handling and recovery
- Resource allocation

### 3. State Manager

The state manager orchestrates workflow execution, manages state transitions, and provides the dashboard for monitoring and debugging.

## Quick Start Example

Create a simple node that processes data:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class SampleNode(BaseNode):
    class Inputs(BaseModel):
        name: str
        data: str

    class Outputs(BaseModel):
        message: str
        processed_data: str

    class Secrets(BaseModel):
        pass

    async def execute(self) -> Outputs:
        print(f"Processing data for: {self.inputs.name}")
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

### Note on blocking behavior of `Runtime.start()`

By design, `Runtime.start()` runs the runtime loop indefinitely and will block the main thread when no asyncio event loop is running (e.g., normal Python scripts). In interactive environments that already have an event loop (like Jupyter notebooks), `Runtime.start()` returns an `asyncio.Task` and does not block.

- If you're in an async/interactive environment (e.g., Jupyter/REPL with a running loop):

  ```python
  # Jupyter/async environment
  runtime = Runtime(namespace="MyProject", name="DataProcessor", nodes=[SampleNode])
  task = runtime.start()  # task is an asyncio.Task running in the background
  # You can continue interacting, and optionally await/cancel the task later
  # await task  # if you want to wait on it
  ```

- If you need a non-blocking start from a regular sync script, run it in a background thread:

  ```python
  from threading import Thread

  runtime = Runtime(namespace="MyProject", name="DataProcessor", nodes=[SampleNode])
  Thread(target=runtime.start, daemon=True).start()
  # continue with other work in the main thread
  ```

- Alternatively, from an async context you can offload to a thread:

  ```python
  import asyncio

  runtime = Runtime(namespace="MyProject", name="DataProcessor", nodes=[SampleNode])
  await asyncio.to_thread(runtime.start)
  ```

## Next Steps

Now that you have the basics, explore:

- **[Register Node](./exosphere/register-node.md)** - Understand how to create and register custom nodes
- **[Create Runtime](./exosphere/create-runtime.md)** - Learn how to set up and configure your runtime
- **[Create Graph](./exosphere/create-graph.md)** - Build workflows by connecting nodes together
- **[Trigger Graph](./exosphere/trigger-graph.md)** - Execute your workflows and monitor their progress

## Key Features

- **Distributed Execution**: Run nodes across multiple compute resources
- **State Management**: Automatic state persistence and recovery
- **Type Safety**: Full Pydantic integration for input/output validation
- **String-only data model (v1)**: All `Inputs`, `Outputs`, and `Secrets` fields are strings
- **Async Support**: Native async/await support for high-performance operations
- **Error Handling**: Built-in retry mechanisms and error recovery
- **Scalability**: Designed for high-volume batch processing and workflows

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Nodes    │    │     Runtime      │    │ State Manager   │
│                 │◄──►│                  │◄──►│                 │
│ - Inputs        │    │ - Registration   │    │ - Orchestration │
│ - Outputs       │    │ - Execution      │    │ - State Mgmt    │
│ - Secrets       │    │ - Error Handling │    │ - Dashboard     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Data Model (v1)

**Important**: In v1, all fields in `Inputs`, `Outputs`, and `Secrets` must be strings. If you need to pass complex data (e.g., JSON), serialize the data to a string first, then parse that string within your node.

```python
class MyNode(BaseNode):
    class Inputs(BaseModel):
        # ✅ Correct - string fields
        user_id: str
        config: str  # JSON string
        
    class Outputs(BaseModel):
        # ✅ Correct - string fields
        result: str
        metadata: str  # JSON string
        
    class Secrets(BaseModel):
        # ✅ Correct - string fields
        api_key: str
        database_url: str
```

## Support

For support and questions:

- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **Documentation**: [https://docs.exosphere.host](https://docs.exosphere.host)
- **GitHub Issues**: [https://github.com/exospherehost/exospherehost/issues](https://github.com/exospherehost/exospherehost/issues)
