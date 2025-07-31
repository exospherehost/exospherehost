# ExosphereHost Python SDK
This SDK is official python SDK for ExosphereHost and interacting with exospherehost.

## Node Creation
You can simply connect to exosphere state manager and start creating your nodes, as shown in sample below: 

```python
from exospherehost import Runtime, BaseNode
import os

class SampleNode(BaseNode):
    async def execute(self, inputs):
        print(inputs)
        return {"message": "success"}

runtime = Runtime("SampleNamespace", os.getenv("EXOSPHERE_STATE_MANAGER_URI", "http://localhost:8000"), os.getenv("EXOSPHERE_API_KEY", ""))

runtime.connect([SampleNode()])
runtime.start()
```

## Support
For first party support and questions do not hesitate to reach out to us at nivedit@exosphere.host