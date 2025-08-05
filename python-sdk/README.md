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

### Basic Node Creation

Create a simple node that processes data:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class SampleNode(BaseNode):
    class Inputs(BaseModel):
        name: str
        data: dict

    class Outputs(BaseModel):
        message: str
        processed_data: dict

    async def execute(self) -> Outputs:
        print(f"Processing data for: {self.inputs.name}")
        # Your processing logic here
        processed_data = {"status": "completed", "input": self.inputs.data}
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
- **Async Support**: Native async/await support for high-performance operations
- **Error Handling**: Built-in retry mechanisms and error recovery
- **Scalability**: Designed for high-volume batch processing and workflows

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
        max_length: int = 100

    class Outputs(BaseModel):
        result: str
        length: int

    async def execute(self) -> Outputs:
        result = self.inputs.text[:self.inputs.max_length]
        return self.Outputs(result=result, length=len(result))
```

### Error Handling

```python
class RobustNode(BaseNode):
    class Inputs(BaseModel):
        data: str

    class Outputs(BaseModel):
        success: bool
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

class APINode(BaseNode):
    class Inputs(BaseModel):
        user_id: str
        query: str

    class Outputs(BaseModel):
        response: dict
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
            response = await client.post(
                f"{self.secrets.api_endpoint}/process",
                headers=headers,
                json={"user_id": self.inputs.user_id, "query": self.inputs.query}
            )
        
        return self.Outputs(
            response=response.json(),
            status="success"
        )
```

**Key points about secrets:**

- **Security**: Secrets are stored securely by the ExosphereHost Runtime and are never exposed in logs or error messages
- **Validation**: The `Secrets` class uses Pydantic for automatic validation of secret values
- **Access**: Secrets are available via `self.secrets` during node execution
- **Types**: Common secret types include API keys, database credentials, encryption keys, and authentication tokens
- **Injection**: Secrets are injected by the Runtime at execution time, so you don't need to handle them manually

## Integration with ExosphereHost Platform

The Python SDK integrates seamlessly with the ExosphereHost platform, providing:

- **Performance**: Optimized execution with intelligent resource allocation and parallel processing
- **Reliability**: Built-in fault tolerance, automatic recovery, and failover capabilities
- **Scalability**: Automatic scaling based on workload demands
- **Monitoring**: Integrated logging and monitoring capabilities

## Documentation

For more detailed information, visit our [documentation](https://docs.exosphere.host).

## Contributing

We welcome contributions! Please see our [contributing guidelines](https://github.com/exospherehost/exospherehost/blob/main/CONTRIBUTING.md) for details.

## Support

For support and questions:
- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **Documentation**: [https://docs.exosphere.host](https://docs.exosphere.host)
- **GitHub Issues**: [https://github.com/exospherehost/exospherehost/issues](https://github.com/exospherehost/exospherehost/issues)

## License

This Python SDK is licensed under the MIT License. The main ExosphereHost project is licensed under the Elastic License 2.0.