import pytest
import asyncio
from pydantic import BaseModel
from exospherehost.node.BaseNode import BaseNode


class ValidNode(BaseNode):
    class Inputs(BaseModel):
        name: str
        count: str

    class Outputs(BaseModel):
        message: str
        result: str

    class Secrets(BaseModel):
        api_key: str
        token: str

    async def execute(self):
        return self.Outputs(
            message=f"Hello {self.inputs.name}", # type: ignore
            result=f"Count: {self.inputs.count}" # type: ignore
        )


class NodeWithListOutput(BaseNode):
    class Inputs(BaseModel):
        items: str

    class Outputs(BaseModel):
        processed: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        count = int(self.inputs.items) # type: ignore
        return [self.Outputs(processed=str(i)) for i in range(count)]


class NodeWithNoneOutput(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        return None


class NodeWithError(BaseNode):
    class Inputs(BaseModel):
        should_fail: str

    class Outputs(BaseModel):
        result: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self):
        if self.inputs.should_fail == "true": # type: ignore
            raise ValueError("Test error")
        return self.Outputs(result="success")


class NodeWithComplexSecrets(BaseNode):
    class Inputs(BaseModel):
        operation: str

    class Outputs(BaseModel):
        status: str

    class Secrets(BaseModel):
        database_url: str
        api_key: str
        encryption_key: str

    async def execute(self):
        return self.Outputs(status=f"Operation {self.inputs.operation} completed") # type: ignore


class TestBaseNodeInitialization:
    def test_base_node_initialization(self):
        # BaseNode is abstract, so we can't instantiate it directly
        # Instead, test that it has the expected attributes
        assert hasattr(BaseNode, 'Inputs')
        assert hasattr(BaseNode, 'Outputs')
        assert hasattr(BaseNode, 'Secrets')
        assert hasattr(BaseNode, 'execute')

    def test_valid_node_initialization(self):
        node = ValidNode()
        assert node.inputs is None
        assert hasattr(node, 'Inputs')
        assert hasattr(node, 'Outputs')
        assert hasattr(node, 'Secrets')

    def test_node_schema_validation(self):
        # Test that Inputs, Outputs, and Secrets are proper Pydantic models
        assert issubclass(ValidNode.Inputs, BaseModel)
        assert issubclass(ValidNode.Outputs, BaseModel)
        assert issubclass(ValidNode.Secrets, BaseModel)

    def test_node_schema_fields(self):
        # Test that all fields are strings as required
        for field_name, field_info in ValidNode.Inputs.model_fields.items():
            assert field_info.annotation is str, f"Input field {field_name} must be str"
        
        for field_name, field_info in ValidNode.Outputs.model_fields.items():
            assert field_info.annotation is str, f"Output field {field_name} must be str"
        
        for field_name, field_info in ValidNode.Secrets.model_fields.items():
            assert field_info.annotation is str, f"Secret field {field_name} must be str"


class TestBaseNodeExecute:
    @pytest.mark.asyncio
    async def test_valid_node_execute(self):
        node = ValidNode()
        inputs = ValidNode.Inputs(name="test_user", count="5")
        secrets = ValidNode.Secrets(api_key="test_key", token="test_token")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert isinstance(result, ValidNode.Outputs)
        assert result.message == "Hello test_user"
        assert result.result == "Count: 5"
        assert node.inputs == inputs
        assert node.secrets == secrets

    @pytest.mark.asyncio
    async def test_node_with_list_output(self):
        node = NodeWithListOutput()
        inputs = NodeWithListOutput.Inputs(items="3")
        secrets = NodeWithListOutput.Secrets(api_key="test_key")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(output, NodeWithListOutput.Outputs) for output in result)
        assert result[0].processed == "0" # type: ignore
        assert result[1].processed == "1" # type: ignore
        assert result[2].processed == "2" # type: ignore

    @pytest.mark.asyncio
    async def test_node_with_none_output(self):
        node = NodeWithNoneOutput()
        inputs = NodeWithNoneOutput.Inputs(name="test")
        secrets = NodeWithNoneOutput.Secrets(api_key="test_key")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert result is None
        assert node.inputs == inputs
        assert node.secrets == secrets

    @pytest.mark.asyncio
    async def test_node_with_error(self):
        node = NodeWithError()
        inputs = NodeWithError.Inputs(should_fail="true")
        secrets = NodeWithError.Secrets(api_key="test_key")
        
        with pytest.raises(ValueError, match="Test error"):
            await node._execute(inputs, secrets) # type: ignore

    @pytest.mark.asyncio
    async def test_node_with_complex_secrets(self):
        node = NodeWithComplexSecrets()
        inputs = NodeWithComplexSecrets.Inputs(operation="backup")
        secrets = NodeWithComplexSecrets.Secrets(
            database_url="postgresql://localhost/db",
            api_key="secret_key",
            encryption_key="encryption_key"
        )
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert isinstance(result, NodeWithComplexSecrets.Outputs)
        assert result.status == "Operation backup completed"
        assert node.secrets == secrets


class TestBaseNodeEdgeCases:
    @pytest.mark.asyncio
    async def test_node_with_empty_strings(self):
        node = ValidNode()
        inputs = ValidNode.Inputs(name="", count="0")
        secrets = ValidNode.Secrets(api_key="", token="")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert result.message == "Hello " # type: ignore
        assert result.result == "Count: 0" # type: ignore

    @pytest.mark.asyncio
    async def test_node_with_special_characters(self):
        node = ValidNode()
        inputs = ValidNode.Inputs(name="test@user.com", count="42")
        secrets = ValidNode.Secrets(api_key="key!@#$%", token="token&*()")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert result.message == "Hello test@user.com" # type: ignore
        assert result.result == "Count: 42" # type: ignore

    @pytest.mark.asyncio
    async def test_node_with_unicode_characters(self):
        node = ValidNode()
        inputs = ValidNode.Inputs(name="José", count="100")
        secrets = ValidNode.Secrets(api_key="🔑", token="🎫")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert result.message == "Hello José" # type: ignore
        assert result.result == "Count: 100" # type: ignore


class TestBaseNodeErrorHandling:
    @pytest.mark.asyncio
    async def test_node_raises_custom_exception(self):
        class NodeWithCustomError(BaseNode):
            class Inputs(BaseModel):
                trigger: str

            class Outputs(BaseModel):
                result: str

            class Secrets(BaseModel):
                api_key: str

            async def execute(self):
                if self.inputs.trigger == "custom": # type: ignore
                    raise RuntimeError("Custom runtime error")
                return self.Outputs(result="ok")

        node = NodeWithCustomError()
        inputs = NodeWithCustomError.Inputs(trigger="custom")
        secrets = NodeWithCustomError.Secrets(api_key="test")
        
        with pytest.raises(RuntimeError, match="Custom runtime error"):
            await node._execute(inputs, secrets) # type: ignore

    @pytest.mark.asyncio
    async def test_node_raises_attribute_error(self):
        class NodeWithAttributeError(BaseNode):
            class Inputs(BaseModel):
                name: str

            class Outputs(BaseModel):
                result: str

            class Secrets(BaseModel):
                api_key: str

            async def execute(self):
                # This will raise AttributeError
                return self.Outputs(result=self.inputs.nonexistent_field) # type: ignore

        node = NodeWithAttributeError()
        inputs = NodeWithAttributeError.Inputs(name="test")
        secrets = NodeWithAttributeError.Secrets(api_key="test")
        
        with pytest.raises(AttributeError):
            await node._execute(inputs, secrets) # type: ignore


class TestBaseNodeAbstractMethods:
    def test_base_node_execute_is_abstract(self):
        # BaseNode should not be instantiable directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseNode() # type: ignore

    def test_concrete_node_implements_execute(self):
        # ValidNode should implement execute
        node = ValidNode()
        # This should not raise NotImplementedError
        assert hasattr(node, 'execute')
        assert callable(node.execute)


class TestBaseNodeModelValidation:
    def test_inputs_validation(self):
        # Test that invalid inputs raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            ValidNode.Inputs(name=123, count="5") # type: ignore

    def test_outputs_validation(self):
        # Test that invalid outputs raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            ValidNode.Outputs(message=123, result="test") # type: ignore

    def test_secrets_validation(self):
        # Test that invalid secrets raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            ValidNode.Secrets(api_key=123, token="test") # type: ignore


class TestBaseNodeConcurrency:
    @pytest.mark.asyncio
    async def test_multiple_concurrent_executions(self):
        node = ValidNode()
        inputs = ValidNode.Inputs(name="test", count="1")
        secrets = ValidNode.Secrets(api_key="key", token="token")
        
        # Run multiple concurrent executions
        tasks = [
            node._execute(inputs, secrets) for _ in range(5) # type: ignore
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, ValidNode.Outputs)
            assert result.message == "Hello test"

    @pytest.mark.asyncio
    async def test_node_with_async_operation(self):
        class AsyncNode(BaseNode):
            class Inputs(BaseModel):
                delay: str

            class Outputs(BaseModel):
                result: str

            class Secrets(BaseModel):
                api_key: str

            async def execute(self):
                delay = float(self.inputs.delay) # type: ignore
                await asyncio.sleep(delay)
                return self.Outputs(result=f"Completed after {delay}s")

        node = AsyncNode()
        inputs = AsyncNode.Inputs(delay="0.1")
        secrets = AsyncNode.Secrets(api_key="test")
        
        result = await node._execute(inputs, secrets) # type: ignore
        
        assert result.result == "Completed after 0.1s" # type: ignore


class TestBaseNodeIntegration:
    @pytest.mark.asyncio
    async def test_node_chain_execution(self):
        # Test that multiple nodes can be executed in sequence
        node1 = ValidNode()
        node2 = NodeWithComplexSecrets()
        
        inputs1 = ValidNode.Inputs(name="user1", count="10")
        secrets1 = ValidNode.Secrets(api_key="key1", token="token1")
        
        inputs2 = NodeWithComplexSecrets.Inputs(operation="process")
        secrets2 = NodeWithComplexSecrets.Secrets(
            database_url="db://test",
            api_key="key2",
            encryption_key="enc2"
        )
        
        result1 = await node1._execute(inputs1, secrets1) # type: ignore
        result2 = await node2._execute(inputs2, secrets2) # type: ignore
        
        assert result1.message == "Hello user1" # type: ignore
        assert result2.status == "Operation process completed" # type: ignore

    @pytest.mark.asyncio
    async def test_node_with_different_output_types(self):
        # Test nodes that return different types of outputs
        node1 = ValidNode()  # Returns single output
        node2 = NodeWithListOutput()  # Returns list of outputs
        node3 = NodeWithNoneOutput()  # Returns None
        
        inputs1 = ValidNode.Inputs(name="test", count="1")
        secrets1 = ValidNode.Secrets(api_key="key", token="token")
        
        inputs2 = NodeWithListOutput.Inputs(items="2")
        secrets2 = NodeWithListOutput.Secrets(api_key="key")
        
        inputs3 = NodeWithNoneOutput.Inputs(name="test")
        secrets3 = NodeWithNoneOutput.Secrets(api_key="key")
        
        result1 = await node1._execute(inputs1, secrets1) # type: ignore
        result2 = await node2._execute(inputs2, secrets2) # type: ignore
        result3 = await node3._execute(inputs3, secrets3) # type: ignore
        
        assert isinstance(result1, ValidNode.Outputs)
        assert isinstance(result2, list)
        assert result3 is None 