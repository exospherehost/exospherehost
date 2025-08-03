# ExosphereHost Python SDK
This is the official Python SDK for ExosphereHost and for interacting with ExosphereHost.

## Node Creation
You can simply connect to exosphere state manager and start creating your nodes, as shown in sample below: 

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class SampleNode(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    async def execute(self, inputs: Inputs) -> Outputs:
        print(inputs)
        return self.Outputs(message="success")

# EXOSPHERE_STATE_MANAGER_URI and EXOSPHERE_API_KEY are required to be set in the environment variables for authentication with exospherehost
runtime = Runtime(
    namespace="SampleNamespace", 
    name="SampleNode"
)

runtime.connect([SampleNode()])
runtime.start()
```

## Support
For first-party support and questions, do not hesitate to reach out to us at <nivedit@exosphere.host>.