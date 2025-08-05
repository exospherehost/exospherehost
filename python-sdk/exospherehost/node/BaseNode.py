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

    class Secrets(BaseModel):
        """
        Secrets schema for the node.

        This class defines the structure for sensitive configuration data that nodes may require
        for their execution. Secrets typically include authentication credentials, API keys,
        database connection strings, encryption keys, and other sensitive information that
        should not be exposed in regular input parameters.

        Subclasses should override this class to define the specific secret fields their node
        requires. The secrets are validated against this schema before node execution and
        are made available to the node via the `self.secrets` attribute during execution.

        Examples of secrets that might be defined:
        - API keys and tokens for external services
        - Database credentials and connection strings
        - Encryption/decryption keys
        - Authentication tokens and certificates
        - Private keys for cryptographic operations

        Note: The actual secret values are managed securely by the Exosphere Runtime
        and are injected into the node at execution time.
        """
        pass

    async def _execute(self, inputs: Inputs, secrets: Secrets) -> Outputs | List[Outputs]:
        """
        Internal method to execute the node with validated inputs and secrets.

        Args:
            inputs (Inputs): The validated input data for this execution.
            secrets (Secrets): The validated secrets data for this execution.

        Returns:
            Outputs | List[Outputs]: The output(s) produced by the node.
        """
        self.inputs = inputs
        self.secrets = secrets
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
