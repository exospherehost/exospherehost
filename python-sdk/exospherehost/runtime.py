import asyncio
import os
from asyncio import Queue, sleep
from typing import List
from .node.BaseNode import BaseNode
from aiohttp import ClientSession
from logging import getLogger

logger = getLogger(__name__)

class Runtime:
    """
    A runtime environment for executing nodes connected to exospherehost.
    
    The Runtime class manages the execution of BaseNode instances in a distributed
    environment. It handles state management, worker coordination, and communication
    with the state manager service.
    
    Attributes:
        _name (str): The name of this runtime instance
        _namespace (str): The namespace this runtime operates in
        _key (str): API key for authentication with the state manager
        _batch_size (int): Number of states to process in each batch
        _connected (bool): Whether the runtime is connected to nodes
        _state_queue (Queue): Queue for managing state processing
        _workers (int): Number of worker tasks to spawn
        _nodes (List[BaseNode]): List of connected node instances
        _node_names (List[str]): List of node unique names
        _state_manager_uri (str): URI of the state manager service
        _state_manager_version (str): Version of the state manager API
        _poll_interval (int): Interval between polling operations in seconds
        _node_mapping (dict): Mapping of node names to node instances
    """

    def __init__(self, namespace: str, name: str, state_manager_uri: str | None = None, key: str | None = None, batch_size: int = 16, workers: int = 4, state_manage_version: str = "v0", poll_interval: int = 1):
        """
        Initialize the Runtime instance.
        
        Args:
            namespace (str): The namespace this runtime operates in
            name (str): The name of this runtime instance
            state_manager_uri (str | None, optional): URI of the state manager service. 
                If None, will be read from EXOSPHERE_STATE_MANAGER_URI environment variable.
            key (str | None, optional): API key for authentication. 
                If None, will be read from EXOSPHERE_API_KEY environment variable.
            batch_size (int, optional): Number of states to process in each batch. Defaults to 16.
            workers (int, optional): Number of worker tasks to spawn. Defaults to 4.
            state_manage_version (str, optional): Version of the state manager API. Defaults to "v0".
            poll_interval (int, optional): Interval between polling operations in seconds. Defaults to 1.
            
        Raises:
            ValueError: If batch_size or workers is less than 1, or if required
                configuration (state_manager_uri, key) is not provided.
        """
        self._name = name
        self._namespace = namespace
        self._key = key
        self._batch_size = batch_size
        self._state_queue = Queue(maxsize=2*batch_size)
        self._workers = workers
        self._nodes = []
        self._node_names = []
        self._state_manager_uri = state_manager_uri
        self._state_manager_version = state_manage_version
        self._poll_interval = poll_interval
        self._node_mapping = {}

        self._set_config_from_env()
        self._validate_runtime()

    def _set_config_from_env(self):
        """Set configuration from environment variables if not provided."""
        if self._state_manager_uri is None:
            self._state_manager_uri = os.environ.get("EXOSPHERE_STATE_MANAGER_URI")
        if self._key is None:
            self._key = os.environ.get("EXOSPHERE_API_KEY")

    def _validate_runtime(self):
        """
        Validate runtime configuration.
        
        Raises:
            ValueError: If batch_size or workers is less than 1, or if required
                configuration (state_manager_uri, key) is not provided.
        """
        if self._batch_size < 1:
            raise ValueError("Batch size should be at least 1")
        if self._workers < 1:
            raise ValueError("Workers should be at least 1")
        if self._state_manager_uri is None:
            raise ValueError("State manager URI is not set")
        if self._key is None:
            raise ValueError("API key is not set")

    def _get_enque_endpoint(self):
        """Get the endpoint URL for enqueueing states."""
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/enqueue"
    
    def _get_executed_endpoint(self, state_id: str):
        """Get the endpoint URL for notifying executed states."""
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/{state_id}/executed"
    
    def _get_errored_endpoint(self, state_id: str):
        """Get the endpoint URL for notifying errored states."""
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/{state_id}/errored"
    
    def _get_register_endpoint(self):
        """Get the endpoint URL for registering nodes with runtime"""
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/nodes/"
    
    async def _register_nodes(self):
        """Register nodes with the runtime"""
        async with ClientSession() as session:
            endpoint = self._get_register_endpoint()
            body = {
                "runtime_name": self._name,
                "runtime_namespace": self._namespace,
                "nodes": [
                    {
                        "name": node.get_unique_name(),
                        "namespace": self._namespace,
                        "inputs_schema": node.Inputs.model_json_schema(),
                        "outputs_schema": node.Outputs.model_json_schema(),
                    } for node in self._nodes
                ]
            }
            headers = {"x-api-key": self._key}
            
            async with session.put(endpoint, json=body, headers=headers) as response: # type: ignore
                res = await response.json()

                if response.status != 200:
                    raise RuntimeError(f"Failed to register nodes: {res}")
                
                return res
                

    async def _register(self, nodes: List[BaseNode]):
        """
        Connect nodes to the runtime.
        
        This method validates and registers the provided nodes with the runtime.
        The nodes will be available for execution when the runtime starts.
        
        Args:
            nodes (List[BaseNode]): List of BaseNode instances to connect
            
        Raises:
            ValueError: If any node does not inherit from BaseNode
        """
        self._nodes = self._validate_nodes(nodes)
        self._node_names = [node.get_unique_name() for node in nodes]
        self._node_mapping = {node.get_unique_name(): node for node in self._nodes}

        await self._register_nodes()


    async def _enqueue_call(self):
        """
        Make an API call to enqueue states from the state manager.
        
        Returns:
            dict: Response from the state manager containing states to process
        """
        async with ClientSession() as session:
            endpoint = self._get_enque_endpoint()
            body = {"nodes": self._node_names, "batch_size": self._batch_size}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response: # type: ignore
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to enqueue states: {res}")
                
                return res

    async def _enqueue(self):
        """
        Continuously enqueue states from the state manager.
        
        This method runs in a loop, polling the state manager for new states
        to process and adding them to the internal queue.
        """
        while True:
            try:
                if self._state_queue.qsize() < self._batch_size: 
                    data = await self._enqueue_call()
                    for state in data["states"]:
                        await self._state_queue.put(state)
            except Exception as e:
                logger.error(f"Error enqueuing states: {e}")
                
            await sleep(self._poll_interval)

    async def _notify_executed(self, state_id: str, outputs: List[BaseNode.Outputs]):
        """
        Notify the state manager that a state has been executed successfully.
        
        Args:
            state_id (str): The ID of the executed state
            outputs (List[BaseNode.Outputs]): The outputs from the node execution
        """
        async with ClientSession() as session:
            endpoint = self._get_executed_endpoint(state_id)
            body = {"outputs": [output.model_dump() for output in outputs]}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response: # type: ignore
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to notify executed state {state_id}: {res}")
      
    async def _notify_errored(self, state_id: str, error: str):
        """
        Notify the state manager that a state has encountered an error.
        
        Args:
            state_id (str): The ID of the errored state
            error (str): The error message
        """
        async with ClientSession() as session:
            endpoint = self._get_errored_endpoint(state_id)
            body = {"error": error}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response: # type: ignore
                res =  await response.json()

                if response.status != 200:
                    logger.error(f"Failed to notify errored state {state_id}: {res}")

    def _validate_nodes(self, nodes: List[BaseNode]):
        """
        Validate that all nodes inherit from BaseNode.
        
        Args:
            nodes (List[BaseNode]): List of nodes to validate
            
        Returns:
            List[BaseNode]: The validated list of nodes
            
        Raises:
            ValueError: If any node does not inherit from BaseNode
        """
        invalid_nodes = []

        for node in nodes:
            if not isinstance(node, BaseNode):
                invalid_nodes.append(f"{node.__class__.__name__}")

        if invalid_nodes:
            raise ValueError(f"Following nodes do not inherit from exospherehost.node.BaseNode: {invalid_nodes}")
        
        return nodes

    async def _worker(self):
        """
        Worker task that processes states from the queue.
        
        This method runs in a loop, taking states from the queue and executing
        the corresponding node. It handles both successful execution and errors.
        """
        while True:
            state = await self._state_queue.get()

            try:
                node = self._node_mapping[state["node_name"]]
                outputs = await node.execute(state["inputs"]) # type: ignore

                if outputs is None:
                    outputs = []

                if isinstance(outputs, BaseNode.Outputs):
                    outputs = [outputs]

                await self._notify_executed(state["state_id"], outputs)
                
            except Exception as e:
                await self._notify_errored(state["state_id"], str(e))

            self._state_queue.task_done() # type: ignore

    async def _start(self, nodes: List[BaseNode]):
        """
        Start the runtime execution.
        
        This method starts the enqueue polling task and spawns worker tasks
        to process states from the queue.
        
        Raises:
            RuntimeError: If the runtime is not connected (no nodes registered)
        """
        await self._register(nodes)
        
        poller = asyncio.create_task(self._enqueue())
        worker_tasks = [asyncio.create_task(self._worker()) for _ in range(self._workers)]

        await asyncio.gather(poller, *worker_tasks)

    def start(self, nodes: List[BaseNode]):
        """
        Start the runtime execution.
        
        This method starts the runtime in the current event loop or creates
        a new one if none exists. It returns a task that can be awaited
        or runs the runtime until completion.
        
        Returns:
            asyncio.Task: The runtime task if running in an existing event loop
        """
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(self._start(nodes))
        except RuntimeError:
            asyncio.run(self._start(nodes))
