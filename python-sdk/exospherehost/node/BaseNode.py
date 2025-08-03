from abc import ABC, abstractmethod
from typing import Any, Optional, List
from pydantic import BaseModel  


class BaseNode(ABC):
    """
    Abstract base class for all nodes in the exospherehost system.
    
    BaseNode provides the foundation for creating executable nodes that can be
    connected to a Runtime for distributed processing. Each node must implement
    the execute method and can optionally define Inputs and Outputs models.
    
    Attributes:
        unique_name (Optional[str]): A unique identifier for this node instance.
            If None, the class name will be used as the unique name.
        state (dict[str, Any]): A dictionary for storing node state between executions.
    """

    def __init__(self, unique_name: Optional[str] = None):
        """
        Initialize a BaseNode instance.
        
        Args:
            unique_name (Optional[str], optional): A unique identifier for this node.
                If None, the class name will be used as the unique name. Defaults to None.
        """
        self.unique_name: Optional[str] = unique_name
        self.state: dict[str, Any] = {}

    class Inputs(BaseModel):
        """
        Pydantic model for defining the input schema of a node.
        
        Subclasses should override this class to define the expected input structure.
        This ensures type safety and validation of inputs before execution.
        """
        pass

    class Outputs(BaseModel):
        """
        Pydantic model for defining the output schema of a node.
        
        Subclasses should override this class to define the expected output structure.
        This ensures type safety and validation of outputs after execution.
        """
        pass

    @abstractmethod
    async def execute(self, inputs: Inputs) -> Outputs | List[Outputs]:
        """
        Execute the node's main logic.
        
        This is the core method that must be implemented by all concrete node classes.
        It receives inputs, processes them according to the node's logic, and returns
        outputs. The method can return either a single Outputs instance or a list
        of Outputs instances for batch processing.
        
        Args:
            inputs (Inputs): The input data for this execution, validated against
                the Inputs model defined by the node.
                
        Returns:
            Outputs | List[Outputs]: The output data from this execution. Can be
                a single Outputs instance or a list of Outputs instances.
                
        Raises:
            Exception: Any exception that occurs during execution will be caught
                by the Runtime and reported as an error state.
        """
        pass

    def get_unique_name(self) -> str:
        """
        Get the unique name for this node instance.
        
        Returns the unique_name if it was provided during initialization,
        otherwise returns the class name.
        
        Returns:
            str: The unique identifier for this node instance
        """
        if self.unique_name is not None:
            return self.unique_name
        return self.__class__.__name__