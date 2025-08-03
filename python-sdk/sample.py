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

runtime = Runtime(
    namespace="SampleNamespace", 
    name="SampleNode"
)

runtime.connect([SampleNode()])
runtime.start()