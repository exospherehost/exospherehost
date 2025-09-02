# Create Runtime

The `Runtime` class is the core component that manages the execution environment for your Exosphere nodes. It handles node registration, state polling, execution, and communication with the state manager.

## Runtime Setup

Before creating a runtime, you need to set up the state manager and configure your environment variables.

### Prerequisites

1. **Start the State Manager**: Run the state manager using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   For detailed setup instructions, see [State Manager Setup](./state-manager-setup.md).

2. **Set Environment Variables**: Configure your authentication:
   ```bash
   export EXOSPHERE_STATE_MANAGER_URI="your-state-manager-uri"
   export EXOSPHERE_API_KEY="your-api-key"
   ```
   
   Or create a `.env` file:
   ```bash
   EXOSPHERE_STATE_MANAGER_URI=your-state-manager-uri
   EXOSPHERE_API_KEY=your-api-key
   ```

### Creating a Runtime
=== "Basic"

    ```python hl_lines="17-22"
    from exospherehost import Runtime, BaseNode
    from pydantic import BaseModel

    class MyNode(BaseNode):
        class Inputs(BaseModel):
            data: str

        class Outputs(BaseModel):
            result: str

        class Secrets(BaseModel):
            pass

        async def execute(self) -> Outputs:
            return self.Outputs(result=f"Processed: {self.inputs.data}")

    # Create and start the runtime
    Runtime(
        namespace="MyProject",
        name="MyRuntime",
        nodes=[MyNode]
    ).start()

    ```

=== "Advanced"

    ```python hl_lines="17-30"
    from exospherehost import Runtime, BaseNode
    from pydantic import BaseModel

    class MyNode(BaseNode):
        class Inputs(BaseModel):
            data: str

        class Outputs(BaseModel):
            result: str

        class Secrets(BaseModel):
            pass

        async def execute(self) -> Outputs:
            return self.Outputs(result=f"Processed: {self.inputs.data}")

    # Create runtime with custom configuration
    runtime = Runtime(
        namespace="MyProject",
        name="MyRuntime",
        nodes=[MyNode],
        state_manager_uri=EXOSPHERE_STATE_MANAGER_URI,
        key=EXOSPHERE_API_KEY,
        batch_size=32,
        workers=8,
        poll_interval=2
    )

    # Start the runtime
    runtime.start()

    ```

!!! warning "Blocking Operation"
    `Runtime.start()` is a blocking operation that runs indefinitely. In interactive environments like Jupyter notebooks, consider running it in a background thread:
    
    ```python
    import threading
    
    def run_runtime():
        runtime.start()
    
    thread = threading.Thread(target=run_runtime, daemon=True)
    thread.start()
    ```
    
    See the [Getting Started guide](../getting-started.md#important-blocking-behavior) for more alternatives.

## Runtime Parameters

### Required Parameters

- **`namespace`** (str): The namespace for your project. Used to organize and isolate your nodes and workflows.
- **`name`** (str): The name of this runtime instance. Must be unique within your namespace.
- **`nodes`** (List[type[BaseNode]]): List of node classes to register and execute.

### Optional Parameters

- **`state_manager_uri`** (str | None): URI of the state manager service. If not provided, uses `EXOSPHERE_STATE_MANAGER_URI` environment variable.
- **`key`** (str | None): API key for authentication. If not provided, uses `EXOSPHERE_API_KEY` environment variable.
- **`batch_size`** (int): Number of states to fetch per poll. Defaults to 16.
- **`workers`** (int): Number of concurrent worker threads. Defaults to 4.
- **`state_manager_version`** (str): State manager API version. Defaults to "v0".
- **`poll_interval`** (int): Seconds between polling for new states. Defaults to 1.

## Environment Configuration

Create a `.env` file in your project root:

```bash
EXOSPHERE_STATE_MANAGER_URI=https://your-state-manager.exosphere.host
EXOSPHERE_API_KEY=your-api-key
```

Then load it in your code:

```python
from dotenv import load_dotenv
load_dotenv()

from exospherehost import Runtime, BaseNode

# Your runtime code here...
```

## Runtime Lifecycle

### 1. Initialization

The runtime validates configuration and node classes:

```python
runtime = Runtime(
    namespace="MyProject",
    name="MyRuntime",
    nodes=[MyNode]
)
```

### 2. Execution

The runtime starts polling for states and executing nodes:

```python
runtime.start()
```

## Multiple Nodes

You can register multiple nodes in a single runtime:

```python hl_lines="10-16"
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class DataProcessorNode(BaseNode):
    ...

class DataValidatorNode(BaseNode):
   ...

# Register both nodes
Runtime(
    namespace="MyProject",
    name="DataPipeline",
    nodes=[DataProcessorNode, DataValidatorNode]
).start()

```

## Runtime Configuration Best Practices

### Batch Size and Workers

Choose appropriate values based on your workload:

```python hl_lines="4 13"
# For CPU-intensive tasks
Runtime(
    namespace="MyProject",
    name="CPU",
    nodes=[MyNode],
    batch_size=8,    # Smaller batches
    workers=2        # Fewer workers
).start()

# For GPU-intensive tasks
Runtime(
    namespace="MyProject",
    name="GPU",
    nodes=[MyNode],
    batch_size=32,   # Larger batches
    workers=16       # More workers
).start()
```

### Poll Interval

Adjust based on your latency requirements:

```python hl_lines="6 14"
# For real-time processing
Runtime(
    namespace="MyProject",
    name="RealTime",
    nodes=[MyNode],
    poll_interval=1  # Poll every second
).start()

# For batch processing
Runtime(
    namespace="MyProject",
    name="Batch",
    nodes=[MyNode],
    poll_interval=10  # Poll every 10 seconds
).start()
```

## Logging

The runtime provides built-in logging:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# The runtime will log:
# - Node registration
# - State polling
# - Execution results
# - Errors and retries
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: exosphere-runtime
spec:
  replicas: 3
  selector:
    matchLabels:
      app: exosphere-runtime
  template:
    metadata:
      labels:
        app: exosphere-runtime
    spec:
      containers:
      - name: runtime
        image: your-registry/exosphere-runtime:latest
        env:
        - name: EXOSPHERE_STATE_MANAGER_URI
          value: "https://your-state-manager.exosphere.host"
        - name: EXOSPHERE_API_KEY
          valueFrom:
            secretKeyRef:
              name: exosphere-secrets
              key: api-key
```

## Monitoring

Monitor your runtime using the Exosphere dashboard:

- **Node Status**: View registered nodes and their health
- **Execution Metrics**: Monitor throughput and error rates
- **State Management**: Track state transitions and completion
- **Error Logs**: Debug failed executions

## Next Steps

- **[Register Node](./register-node.md)** - Learn how to create custom nodes
- **[Create Graph](./create-graph.md)** - Build workflows by connecting nodes
- **[Trigger Graph](./trigger-graph.md)** - Execute and monitor workflows
