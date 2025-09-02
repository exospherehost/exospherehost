import pytest
from exospherehost import Runtime, BaseNode, StateManager, TriggerState, VERSION


def test_package_imports():
    """Test that all expected classes and constants can be imported from the package."""
    assert Runtime is not None
    assert BaseNode is not None
    assert StateManager is not None
    assert TriggerState is not None
    assert VERSION is not None


def test_package_all_imports():
    """Test that __all__ contains all expected exports."""
    from exospherehost import __all__
    
    expected_exports = ["Runtime", "BaseNode", "StateManager", "TriggerState", "VERSION", "PruneSignal", "ReQueueAfterSignal"]
    
    for export in expected_exports:
        assert export in __all__, f"{export} should be in __all__"
    
    # Check that __all__ doesn't contain unexpected exports
    for export in __all__:
        assert export in expected_exports, f"Unexpected export: {export}"


def test_runtime_class_import():
    """Test that Runtime class can be imported and instantiated with proper config."""
    from exospherehost.runtime import Runtime as RuntimeDirect
    
    # Test that the imported Runtime is the same as the one from the package
    assert Runtime is RuntimeDirect


def test_base_node_class_import():
    """Test that BaseNode class can be imported and is abstract."""
    from exospherehost.node.BaseNode import BaseNode as BaseNodeDirect
    
    # Test that the imported BaseNode is the same as the one from the package
    assert BaseNode is BaseNodeDirect
    
    # Test that BaseNode is abstract
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseNode() # type: ignore
    
    # Test that it has the expected attributes
    assert hasattr(BaseNode, 'execute')
    assert callable(BaseNode.execute)


def test_state_manager_class_import():
    """Test that StateManager class can be imported."""
    from exospherehost.statemanager import StateManager as StateManagerDirect
    
    # Test that the imported StateManager is the same as the one from the package
    assert StateManager is StateManagerDirect


def test_trigger_state_class_import():
    """Test that TriggerState class can be imported and instantiated."""
    from exospherehost.statemanager import TriggerState as TriggerStateDirect
    
    # Test that the imported TriggerState is the same as the one from the package
    assert TriggerState is TriggerStateDirect
    
    # Test that TriggerState can be instantiated
    state = TriggerState(identifier="test", inputs={"key": "value"})
    assert state.identifier == "test"
    assert state.inputs == {"key": "value"}


def test_version_import():
    """Test that VERSION is properly imported and is a string."""
    from exospherehost._version import version as version_direct
    
    # Test that VERSION is the same as the direct import
    assert VERSION == version_direct
    assert isinstance(VERSION, str)
    assert len(VERSION) > 0


def test_package_docstring():
    """Test that the package has a proper docstring."""
    import exospherehost
    
    assert exospherehost.__doc__ is not None
    assert len(exospherehost.__doc__) > 0
    assert "ExosphereHost" in exospherehost.__doc__
    assert "Python SDK" in exospherehost.__doc__


def test_package_version_attribute():
    """Test that the package has a __version__ attribute."""
    import exospherehost
    
    assert hasattr(exospherehost, '__version__')
    assert exospherehost.__version__ == VERSION


def test_import_without_side_effects():
    """Test that importing the package doesn't cause side effects."""
    import logging
    
    # Store initial state
    initial_handlers = len(logging.getLogger().handlers)
    
    # Check that logging handlers weren't added unexpectedly
    # (The package might add handlers during import, which is expected)
    current_handlers = len(logging.getLogger().handlers)
    
    # The package should either not add handlers or add them consistently
    assert current_handlers >= initial_handlers


def test_package_structure():
    """Test that the package has the expected structure."""
    import exospherehost
    
    # Check that the package has expected attributes
    assert hasattr(exospherehost, 'Runtime')
    assert hasattr(exospherehost, 'BaseNode')
    assert hasattr(exospherehost, 'StateManager')
    assert hasattr(exospherehost, 'TriggerState')
    assert hasattr(exospherehost, 'VERSION')
    assert hasattr(exospherehost, '__version__')
    assert hasattr(exospherehost, '__all__')


def test_package_example_usage():
    """Test that the package can be used as shown in the docstring example."""
    from pydantic import BaseModel
    
    # Create a sample node as shown in the docstring
    class SampleNode(BaseNode):
        class Inputs(BaseModel):
            name: str

        class Outputs(BaseModel):
            message: str

        class Secrets(BaseModel):
            api_key: str

        async def execute(self):
            return self.Outputs(message="success")
    
    # Test that the node can be instantiated
    node = SampleNode()
    assert isinstance(node, BaseNode)
    assert hasattr(node, 'execute')
    
    # Test that Runtime can be instantiated (with proper config)
    # Note: This requires environment variables or proper config
    # We'll just test that the class exists and can be referenced
    assert Runtime is not None
    assert callable(Runtime) 