import pytest
import warnings
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
		return self.Outputs(message=f"hi {self.inputs.name}") # type: ignore


class BadNodeWrongInputsBase(BaseNode):
	Inputs = object  # not a pydantic BaseModel # type: ignore
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


@pytest.mark.filterwarnings("ignore:.*coroutine.*was never awaited.*:RuntimeWarning")
def test_runtime_with_env_ok(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	rt = Runtime(namespace="ns", name="rt", nodes=[GoodNode])
	assert rt is not None


@pytest.mark.filterwarnings("ignore:.*coroutine.*was never awaited.*:RuntimeWarning")
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


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.filterwarnings("ignore:.*coroutine.*was never awaited.*:RuntimeWarning")
def test_duplicate_node_names_raise(monkeypatch):
	monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
	monkeypatch.setenv("EXOSPHERE_API_KEY", "k")
	
	# Create two classes with the same name using a different approach
	class GoodNode1(BaseNode):
		class Inputs(BaseModel):
			name: str
		class Outputs(BaseModel):
			message: str
		class Secrets(BaseModel):
			api_key: str
		async def execute(self):
			return self.Outputs(message="ok")
	
	class GoodNode2(BaseNode):
		class Inputs(BaseModel):
			name: str
		class Outputs(BaseModel):
			message: str
		class Secrets(BaseModel):
			api_key: str
		async def execute(self):
			return self.Outputs(message="ok")
	
	# Use the same name for both classes
	GoodNode2.__name__ = "GoodNode1"
	
	# Suppress warnings about unawaited coroutines and pytest unraisable exceptions (test-only)
	with warnings.catch_warnings():
		warnings.filterwarnings(
			"ignore",
			message=".*coroutine.*was never awaited.*",
			category=RuntimeWarning
		)
		warnings.filterwarnings(
			"ignore",
			category=pytest.PytestUnraisableExceptionWarning
		)
		with pytest.raises(ValueError):
			Runtime(namespace="ns", name="rt", nodes=[GoodNode1, GoodNode2])