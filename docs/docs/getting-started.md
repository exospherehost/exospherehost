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

> **🔐 Authentication**: When making API requests to the state-manager, the `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value in the state-manager container.

## Overview

Exosphere is built around several core concepts that enable powerful workflow orchestration:

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant Runtime as Runtime
    participant Node as Node Executor
    participant StateMgr as State Manager
    participant MongoDB as State Store
    
    Client->>Runtime: Initialize with nodes
    Runtime->>StateMgr: Register runtime & nodes
    StateMgr->>MongoDB: Store registration info
    
    loop Workflow Execution
        StateMgr->>Runtime: Trigger node execution
        Runtime->>Node: Execute node logic
        Node->>Runtime: Return outputs
        Runtime->>StateMgr: Update execution state
        StateMgr->>MongoDB: Persist state changes
        StateMgr->>Runtime: Trigger next node (if any)
    end
    
    StateMgr->>Client: Return final results
```

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

### 4. Core Concepts

Exosphere provides several unique features that make it powerful:

- **[Fanout](./exosphere/fanout.md)**: Create parallel execution paths dynamically
- **[Unite](./exosphere/unite.md)**: Synchronize parallel execution paths
- **[Signals](./exosphere/signals.md)**: Control workflow execution flow
- **[Retry Policy](./exosphere/retry-policy.md)**: Build resilient workflows
- **[Store](./exosphere/store.md)**: Persist data across workflow execution

For a comprehensive overview, see **[Exosphere Concepts](./exosphere/concepts.md)**.

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

## Important: Blocking Behavior

**Note**: `Runtime.start()` is a blocking operation that will run indefinitely until stopped. This can be problematic in interactive environments like Jupyter notebooks or Python REPLs.

### For Interactive Environments

If you're working in a Jupyter notebook or Python REPL, consider these alternatives:

=== "Background Thread"

    ```python
    import threading
    
    # Create the runtime
    runtime = Runtime(
        namespace="MyProject",
        name="DataProcessor",
        nodes=[SampleNode]
    )
    
    # Run in a background thread
    def run_runtime():
        runtime.start()
    
    thread = threading.Thread(target=run_runtime, daemon=True)
    thread.start()
    
    # Your interactive session continues here
    print("Runtime is running in the background!")
    ```

=== "Asyncio Task (Jupyter/Async Context)"

    ```python
    import asyncio
    
    # Create the runtime
    runtime = Runtime(
        namespace="MyProject",
        name="DataProcessor",
        nodes=[SampleNode]
    )
    
    # In Jupyter notebooks or async contexts, use asyncio.create_task
    # to run the runtime in the background
    runtime_task = asyncio.create_task(runtime._start())
    
    # Your interactive session can continue
    print("Runtime is running in the background!")
    
    # You can now do other async work while the runtime runs
    # For example:
    await asyncio.sleep(1)
    print("Runtime is still running...")
    
    # To stop the runtime later:
    # runtime_task.cancel()
    ```

=== "Production Script"

    ```python
    # For production scripts, the blocking behavior is usually desired
    if __name__ == "__main__":
        Runtime(
            namespace="MyProject",
            name="DataProcessor",
            nodes=[SampleNode]
        ).start()  # Blocks and runs forever
    ```


## Key Features

- **Distributed Execution**: Run nodes across multiple compute resources
- **State Management**: Automatic state persistence and recovery
- **Type Safety**: Full Pydantic integration for input/output validation
- **String-only data model (v1)**: All `Inputs`, `Outputs`, and `Secrets` fields are strings
- **Async Support**: Native async/await support for high-performance operations
- **Error Handling**: Built-in retry mechanisms and error recovery
- **Scalability**: Designed for high-volume batch processing and workflows

## Next Steps

Now that you have the basics, explore:

- **[Local Setup](./exosphere/local-setup.md)** - Set up Exosphere locally for development and testing
- **[Register Node](./exosphere/register-node.md)** - Understand how to create and register custom nodes
- **[Create Runtime](./exosphere/create-runtime.md)** - Learn how to set up and configure your runtime
- **[Create Graph](./exosphere/create-graph.md)** - Build workflows by connecting nodes together
- **[Trigger Graph](./exosphere/trigger-graph.md)** - Execute your workflows and monitor their progress




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
