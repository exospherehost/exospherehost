"""
Node module for the exospherehost package.

This module contains the core node-related components for building executable
workflow nodes. The main component is BaseNode, which provides the foundation
for creating custom nodes that can be executed by the Runtime.

Components:
- BaseNode: Abstract base class for all executable nodes
- Status constants: Define the various states in workflow execution
"""

from .BaseNode import BaseNode
from .status import Status

__all__ = ["BaseNode", "Status"]
