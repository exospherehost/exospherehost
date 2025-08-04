from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel  


class BaseNode(ABC):
    """
    Abstract base class for all nodes in the exospherehost system.

    This class defines the interface and structure for executable nodes that can be
    managed by an Exosphere Runtime. Subclasses should define their own `Inputs` and
    `Outputs` models (as subclasses of pydantic.BaseModel) to specify the input and
    output schemas for the node, and must implement the `execute` method containing
    the node's main logic.

    Attributes:
        inputs (Optional[BaseNode.Inputs]): The validated input data for the node execution.
    """

    def __init__(self):
        """
        Initialize a BaseNode instance.

        Sets the `inputs` attribute to None. The `inputs` attribute will be populated
        with validated input data before execution.
        """
        self.inputs: Optional[BaseNode.Inputs] = None

    class Inputs(BaseModel):
        """
        Input schema for the node.

        Subclasses should override this class to define the expected input fields.
        """
        pass

    class Outputs(BaseModel):
        """
        Output schema for the node.

        Subclasses should override this class to define the expected output fields.
        """
        pass

    async def _execute(self, inputs: Inputs) -> Outputs | List[Outputs]:
        """
        Internal method to execute the node with validated inputs.

        Args:
            inputs (Inputs): The validated input data for this execution.

        Returns:
            Outputs | List[Outputs]: The output(s) produced by the node.
        """
        self.inputs = inputs
        return await self.execute()

    @abstractmethod
    async def execute(self) -> Outputs | List[Outputs]:
        """
        Main logic for the node.

        This method must be implemented by all subclasses. It should use `self.inputs`
        (populated with validated input data) to perform the node's computation and
        return either a single Outputs instance or a list of Outputs instances.

        Returns:
            Outputs | List[Outputs]: The output(s) produced by the node.

        Raises:
            Exception: Any exception raised here will be caught and reported as an error state by the Runtime.
        """
        raise NotImplementedError("execute method must be implemented by all concrete node classes")
