# Exosphere Docs



Exosphere is an open-source infrastructure layer to run distributed AI workflows and agents with Python based on a node-based architecture.

---

**Documentation**: [https://docs.exosphere.host](https://docs.exosphere.host)

**Source Code**: [https://github.com/exospherehost/exospherehost](https://github.com/exospherehost/exospherehost)

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

### Create it

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

### Run it

Run the server with:

```bash
uv run main.py
```

### Check it

Your runtime is now running and ready to process workflows!

### Interactive Dashboard

Now go to your Exosphere dashboard to:

* View your registered nodes
* Create and manage graph templates
* Trigger workflows
* Monitor execution states
* Debug and troubleshoot

Ref: [Dashboard Guide](./exosphere/dashboard.md)

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

### Create it

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
).start()
```

### Run it

Run the server with:

```bash
uv run main.py
```

### Check it

Your runtime is now running and ready to process workflows!

### Interactive Dashboard

Now go to your Exosphere dashboard to:

* View your registered nodes
* Create and manage graph templates
* Trigger workflows
* Monitor execution states
* Debug and troubleshoot

Ref: [Dashboard Guide](./exosphere/dashboard.md)

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


