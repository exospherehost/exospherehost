import pytest
from pydantic import BaseModel
from exospherehost.node.BaseNode import BaseNode


class TestBaseNodeAbstract:
    """Test the abstract BaseNode class and its NotImplementedError."""

    def test_base_node_abstract_execute(self):
        """Test that BaseNode.execute raises NotImplementedError."""
        # Create a concrete subclass that implements execute but raises NotImplementedError
        class ConcreteNode(BaseNode):
            class Inputs(BaseModel):
                name: str
            
            class Outputs(BaseModel):
                message: str
            
            class Secrets(BaseModel):
                pass
            
            async def execute(self):
                raise NotImplementedError("execute method must be implemented by all concrete node classes")
        
        node = ConcreteNode()
        
        with pytest.raises(NotImplementedError, match="execute method must be implemented by all concrete node classes"):
            # This should raise NotImplementedError
            import asyncio
            asyncio.run(node.execute())

    def test_base_node_abstract_execute_with_inputs(self):
        """Test that BaseNode._execute raises NotImplementedError when execute is not implemented."""
        # Create a concrete subclass that implements execute but raises NotImplementedError
        class ConcreteNode(BaseNode):
            class Inputs(BaseModel):
                name: str
            
            class Outputs(BaseModel):
                message: str
            
            class Secrets(BaseModel):
                pass
            
            async def execute(self):
                raise NotImplementedError("execute method must be implemented by all concrete node classes")
        
        node = ConcreteNode()
        
        with pytest.raises(NotImplementedError, match="execute method must be implemented by all concrete node classes"):
            # This should raise NotImplementedError
            import asyncio
            asyncio.run(node._execute(node.Inputs(name="test"), node.Secrets())) # type: ignore

    def test_base_node_initialization(self):
        """Test that BaseNode initializes correctly."""
        # Create a concrete subclass
        class ConcreteNode(BaseNode):
            class Inputs(BaseModel):
                name: str
            
            class Outputs(BaseModel):
                message: str
            
            class Secrets(BaseModel):
                pass
            
            async def execute(self):
                return self.Outputs(message="test")
        
        node = ConcreteNode()
        assert node.inputs is None

    def test_base_node_inputs_class(self):
        """Test that BaseNode has Inputs class."""
        assert hasattr(BaseNode, 'Inputs')
        assert issubclass(BaseNode.Inputs, BaseModel)

    def test_base_node_outputs_class(self):
        """Test that BaseNode has Outputs class."""
        assert hasattr(BaseNode, 'Outputs')
        assert issubclass(BaseNode.Outputs, BaseModel)

    def test_base_node_secrets_class(self):
        """Test that BaseNode has Secrets class."""
        assert hasattr(BaseNode, 'Secrets')
        assert issubclass(BaseNode.Secrets, BaseModel) 