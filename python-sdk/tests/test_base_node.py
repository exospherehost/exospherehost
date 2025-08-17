from exospherehost.node.BaseNode import BaseNode
from pydantic import BaseModel
import asyncio


class EchoNode(BaseNode):
	class Inputs(BaseModel):
		text: str

	class Outputs(BaseModel):
		message: str

	class Secrets(BaseModel):
		token: str

	async def execute(self) -> Outputs:
		return self.Outputs(message=f"{self.inputs.text}:{self.secrets.token}")


def test_base_node_execute_sets_inputs_and_returns_outputs():
	node = EchoNode()
	inputs = EchoNode.Inputs(text="hello")
	secrets = EchoNode.Secrets(token="tkn")
	outputs = asyncio.run(node._execute(inputs, secrets))

	assert isinstance(outputs, EchoNode.Outputs)
	assert outputs.message == "hello:tkn"
	assert node.inputs == inputs
	assert node.secrets == secrets