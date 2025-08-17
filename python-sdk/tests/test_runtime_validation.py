import pytest
from pydantic import BaseModel
from exospherehost.runtime import Runtime
from exospherehost.node.BaseNode import BaseNode


class GoodNode(BaseNode):
	class Inputs(BaseModel):
		name: str

	class Outputs(BaseModel):
		message: str

	class Secrets(BaseModel):
		api_key: str

	async def execute(self):
		return self.Outputs(message=f"hi {self.inputs.name}")


class BadNodeWrongInputsBase(BaseNode):
	Inputs = object  # not a pydantic BaseModel
	class Outputs(BaseModel):
		message: str
	class Secrets(BaseModel):
		token: str
	async def execute(self):
		return self.Outputs(message="x")


class BadNodeWrongTypes(BaseNode):
	class Inputs(BaseModel):
		count: int
	class Outputs(BaseModel):
		ok: bool
	class Secrets(BaseModel):
		secret: bytes
	async def execute(self):
		return self.Outputs(ok=True)




def test_runtime_missing_config_raises(monkeypatch):
	# Ensure env vars not set
	monkeypatch.delenv("EXOSPHERE_STATE_MANAGER_URI", raising=False)
	monkeypatch.delenv("EXOSPHERE_API_KEY", raising=False)
	with pytest.raises(ValueError):
		Runtime(namespace="ns", name="rt", nodes=[GoodNode])


def test_runtime_with_env_ok(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	rt = Runtime(namespace="ns", name="rt", nodes=[GoodNode])
	assert rt is not None


def test_runtime_invalid_params_raises(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	with pytest.raises(ValueError):
		Runtime(namespace="ns", name="rt", nodes=[GoodNode], batch_size=0)
	with pytest.raises(ValueError):
		Runtime(namespace="ns", name="rt", nodes=[GoodNode], workers=0)


def test_node_validation_errors(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	with pytest.raises(ValueError) as e:
		Runtime(namespace="ns", name="rt", nodes=[BadNodeWrongInputsBase])
	assert "Inputs class that inherits" in str(e.value)

	with pytest.raises(ValueError) as e2:
		Runtime(namespace="ns", name="rt", nodes=[BadNodeWrongTypes])
	msg = str(e2.value)
	assert "Inputs field" in msg and "Outputs field" in msg and "Secrets field" in msg


def test_duplicate_node_names_raise(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	class AnotherGood(BaseNode):
		class Inputs(BaseModel):
			name: str
		class Outputs(BaseModel):
			message: str
		class Secrets(BaseModel):
			api_key: str
		async def execute(self):
			return self.Outputs(message="ok")
	AnotherGood.__name__ = "GoodNode"  # force duplicate name
	with pytest.raises(ValueError):
		Runtime(namespace="ns", name="rt", nodes=[GoodNode, AnotherGood])