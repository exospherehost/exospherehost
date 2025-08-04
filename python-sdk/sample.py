from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class SampleNode(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    async def execute(self) -> Outputs:
        print(self.inputs)
        return self.Outputs(message="success")

Runtime(
    namespace="SampleNamespace", 
    name="SampleRuntime",
    nodes=[SampleNode]
).start()