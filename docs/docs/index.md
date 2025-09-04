![exosphere logo](assets/logo-with-bg.png)

<p align="center">
  <a href="https://docs.exosphere.host"><img src="https://img.shields.io/badge/docs-latest-success" alt="Docs"></a>
  <a href="https://github.com/exospherehost/exospherehost/commits/main"><img src="https://img.shields.io/github/last-commit/exospherehost/exospherehost" alt="Last commit"></a>
  <a href="https://pypi.org/project/exospherehost/"><img src="https://img.shields.io/pypi/v/exospherehost" alt="PyPI - Version"></a>
  <a href="https://codecov.io/gh/exospherehost/exospherehost"><img src="https://img.shields.io/codecov/c/gh/exospherehost/exospherehost" alt="Coverage"></a>
  <a href="https://github.com/orgs/exospherehost/packages?repo_name=exospherehost"><img src="https://img.shields.io/badge/Kubernetes-native-326ce5?logo=kubernetes&logoColor=white" alt="Kubernetes"></a>
  <a href="https://discord.com/invite/zT92CAgvkj"><img src="https://badgen.net/discord/members/zT92CAgvkj" alt="Discord"></a>
  <a href="https://github.com/exospherehost/exospherehost"><img src="https://img.shields.io/github/stars/exospherehost/exospherehost?style=social" alt="Stars"></a>
</p>


# Exosphere: Distributed AI Workflow Infrastructure

**Exosphere** is an open-source, Kubernetes-native infrastructure platform designed to run distributed AI workflows and autonomous agents at scale. Built with Python and based on a flexible node-based architecture, Exosphere enables developers to create, deploy, and manage robust AI workflows that can handle large-scale data processing and long-running operations.

## What Exosphere Can Do

Exosphere provides a powerful foundation for building and orchestrating AI applications with these key capabilities:

### **Scalable AI Workflows**
- **Infinite Parallel Agents**: Run multiple AI agents simultaneously across distributed infrastructure
- **Dynamic State Management**: Create and manage state at runtime with persistent storage
- **Fault Tolerance**: Built-in failure handling and recovery mechanisms for production reliability

### **Developer Experience**
- **Plug-and-Play Nodes**: Create reusable, atomic workflow components that can be mixed and matched
- **Python-First**: Native Python support with Pydantic models for type-safe inputs/outputs

### **Production Infrastructure**
- **Kubernetes Native**: Deploy seamlessly on Kubernetes clusters for enterprise-grade scalability
- **State Persistence**: Maintain workflow state across restarts and failures
- **Interactive Dashboard**: Visual workflow management, monitoring, and debugging tools

### **AI Agent Capabilities**
- **Autonomous Execution**: Build agents that can make decisions and execute complex workflows
- **Data Processing**: Handle large datasets with distributed processing capabilities
- **API Integration**: Connect to external services and APIs through configurable nodes

Whether you're building data pipelines, AI agents, or complex workflow orchestrations, Exosphere provides the infrastructure backbone to make your AI applications production-ready and scalable.

---

**Watch the Step by Step Demo**:

<a href="https://www.youtube.com/watch?v=f41UtzInhp8" target="_blank">
  <img src="../assets/parallel-nodes-demo.png" alt="Step by Step Execution of an Exosphere Workflow">
</a>


---

## Requirements

Python 3.12+

## Installation

```bash
uv add exospherehost
```

## Example

### Create

Create a file `main.py` with:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class HelloWorldNode(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        pass

    async def execute(self) -> Outputs:
        return self.Outputs(
            message=f"Hello, {self.inputs.name}!"
        )

# Initialize the runtime
Runtime(
    namespace="MyProject",
    name="HelloWorld",
    nodes=[HelloWorldNode]
).start()  # Note: This blocks the main thread
```

!!! info "Interactive Environments"
    If you're using Jupyter notebooks or Python REPLs, `Runtime.start()` will block your session. See the [Getting Started guide](./getting-started.md#important-blocking-behavior) for non-blocking alternatives.

### Run

Run the server with:

```bash
uv run main.py
```

### Check

Your runtime is now running and ready to process workflows!


### Local Development

Get the Exosphere State Manager and Dashboard ready to start building workflows locally.

Ref: [Local Setup](./local-setup.md)

## Example graph

Now modify the file `main.py` to add more complex processing:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel
import json

class DataProcessorNode(BaseNode):
    class Inputs(BaseModel):
        data: str
        operation: str

    class Outputs(BaseModel):
        result: str
        status: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self) -> Outputs:
        # Parse the input data
        try:
            data = json.loads(self.inputs.data)
        except:
            return self.Outputs(
                result="",
                status="error: invalid json"
            )
        
        # Process based on operation
        if self.inputs.operation == "transform":
            result = {"transformed": data, "processed": True}
        else:
            result = {"original": data, "processed": False}
        
        return self.Outputs(
            result=json.dumps(result),
            status="success"
        )

# Initialize the runtime
Runtime(
    namespace="MyProject",
    name="DataProcessor",
    nodes=[DataProcessorNode]
).start()
```

The runtime will automatically reload and register the updated node.


## Open Source Commitment

We believe that humanity would not have been able to achieve the level of innovation and progress we have today without the support of open source and community, we want to be a part of this movement and support the open source community. In following ways: 

1. We will be open sourcing majority of our codebase for exosphere.host and making it available to the community. We welcome all sort of contributions and feedback from the community and will be happy to collaborate with you.
2. For whatever the profits which we generate from exosphere.host, we will be donating a portion of it to open source projects and communities. If you have any questions, suggestions or ideas.
3. We would be further collaborating with various open source student programs to provide with the support and encourage and mentor the next generation of open source contributors.

Please feel free to reach out to us at [nivedit@exosphere.host](mailto:nivedit@exosphere.host). Lets push the boundaries of possibilities for humanity together!

## Contributing

We welcome community contributions. For guidelines, refer to our [CONTRIBUTING.md](https://github.com/exospherehost/exospherehost/blob/main/CONTRIBUTING.md).

![exosphere.host Contributors](https://contrib.rocks/image?repo=exospherehost/exospherehost)


