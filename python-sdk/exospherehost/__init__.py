"""
ExosphereHost Python SDK

A distributed workflow execution framework for building scalable, stateful applications.

This package provides the core components for creating and executing distributed
workflows using a node-based architecture. The main components are:

- Runtime: Manages the execution environment and coordinates with the state manager
- BaseNode: Abstract base class for creating executable nodes
- Status constants: Define the various states in the workflow lifecycle

Example usage:
    from exospherehost import Runtime, BaseNode
    
    # Create a custom node
    class MyNode(BaseNode):
        class Inputs(BaseModel):
            data: str
            
        class Outputs(BaseModel):
            result: str
            
        async def execute(self, inputs: Inputs) -> Outputs:
            return Outputs(result=f"Processed: {inputs.data}")
    
    # Create and start runtime
    runtime = Runtime(namespace="my-namespace", name="my-runtime")
    runtime.connect([MyNode()])
    runtime.start()
"""

from ._version import version as __version__
from .runtime import Runtime
from .node.BaseNode import BaseNode

VERSION = __version__

__all__ = ["Runtime", "BaseNode", "VERSION"]