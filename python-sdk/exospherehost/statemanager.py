import os
import aiohttp
from pydantic import BaseModel


class TriggerState(BaseModel):
    """
    Represents a trigger state for graph execution.
    
    A trigger state contains an identifier and a set of input parameters that
    will be passed to the graph when it is triggered for execution.
    
    Attributes:
        identifier (str): A unique identifier for this trigger state. This is used
            to distinguish between different trigger states and may be used by the
            graph to determine how to process the trigger.
        inputs (dict[str, str]): A dictionary of input parameters that will be
            passed to the graph. The keys are parameter names and values are
            parameter values, both as strings.
    
    Example:
        ```python
        # Create a trigger state with identifier and inputs
        trigger_state = TriggerState(
            identifier="user-login",
            inputs={
                "user_id": "12345",
                "session_token": "abc123def456",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )
        ```
    """
    identifier: str
    inputs: dict[str, str]


class StateManager:

    def __init__(self, namespace: str, state_manager_uri: str | None = None, key: str | None = None, state_manager_version: str = "v0"):
        self._state_manager_uri = state_manager_uri
        self._key = key
        self._state_manager_version = state_manager_version
        self._namespace = namespace

        self._set_config_from_env()

    def _set_config_from_env(self):
        """
        Set configuration from environment variables if not provided.
        """
        if self._state_manager_uri is None:
            self._state_manager_uri = os.environ.get("EXOSPHERE_STATE_MANAGER_URI")
        if self._key is None:
            self._key = os.environ.get("EXOSPHERE_API_KEY")

    def _get_trigger_state_endpoint(self, graph_name: str):
        return f"{self._state_manager_uri}/{self._state_manager_version}/namespace/{self._namespace}/graph/{graph_name}/trigger"

    async def trigger(self, graph_name: str, state: TriggerState | None = None, states: list[TriggerState] | None = None):
        """
        Trigger a graph execution with one or more trigger states.
        
        This method sends trigger states to the specified graph endpoint to initiate
        graph execution. It accepts either a single trigger state or a list of trigger
        states, but not both simultaneously.
        
        Args:
            graph_name (str): The name of the graph to trigger execution for.
            state (TriggerState | None, optional): A single trigger state to send.
                Must be provided if `states` is None.
            states (list[TriggerState] | None, optional): A list of trigger states to send.
                Must be provided if `state` is None. Cannot be an empty list.
        
        Returns:
            dict: The JSON response from the state manager API containing the
                result of the trigger operation.
        
        Raises:
            ValueError: If neither `state` nor `states` is provided, if both are provided,
                or if `states` is an empty list.
            Exception: If the API request fails with a non-200 status code. The exception
                message includes the HTTP status code and response text for debugging.
        
        Example:
            ```python
            # Trigger with a single state
            state = TriggerState(identifier="my-trigger", inputs={"key": "value"})
            result = await state_manager.trigger("my-graph", state=state)
            
            # Trigger with multiple states
            states = [
                TriggerState(identifier="trigger1", inputs={"key1": "value1"}),
                TriggerState(identifier="trigger2", inputs={"key2": "value2"})
            ]
            result = await state_manager.trigger("my-graph", states=states)
            ```
        """
        if state is None and states is None:
            raise ValueError("Either state or states must be provided")
        if state is not None and states is not None:
            raise ValueError("Only one of state or states must be provided")
        if states is not None and len(states) == 0:
            raise ValueError("States must be a non-empty list")
        
        states_list = []
        if state is not None:
            states_list.append(state)
        if states is not None:
            states_list.extend(states)

        body = {
            "states": [state.model_dump() for state in states_list]
        }
        headers = {
            "x-api-key": self._key
        }
        endpoint = self._get_trigger_state_endpoint(graph_name)
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=body, headers=headers) as response: # type: ignore
                if response.status != 200:
                    raise Exception(f"Failed to trigger state: {response.status} {await response.text()}")
                return await response.json()
