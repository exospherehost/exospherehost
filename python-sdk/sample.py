from exospherehost import Runtime, BaseNode
import os

class SampleNode(BaseNode):
    async def execute(self, inputs):
        print(inputs)
        return {"message": "success"}

runtime = Runtime("SampleNamespace", os.getenv("EXOSPHERE_STATE_MANAGER_URI", "http://localhost:8000"), os.getenv("EXOSPHERE_API_KEY", ""))

runtime.connect([SampleNode()])
runtime.start()