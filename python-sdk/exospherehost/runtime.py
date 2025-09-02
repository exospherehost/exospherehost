import asyncio
import os
import logging
import traceback

from asyncio import Queue, sleep
from typing import List, Dict
from pydantic import BaseModel
from .node.BaseNode import BaseNode
from aiohttp import ClientSession
from .signals import PruneSignal, ReQueueAfterSignal

logger = logging.getLogger(__name__)

def _setup_default_logging():
    """
    Setup default logging only if no handlers are configured.
    Respects user's existing logging configuration.
    """
    root_logger = logging.getLogger()
    
    # Don't interfere if user has already configured logging
    if root_logger.handlers:
        return
    
    # Allow users to disable default logging
    if os.environ.get('EXOSPHERE_DISABLE_DEFAULT_LOGGING'):
        return
    
    # Get log level from environment or default to INFO
    log_level_name = os.environ.get('EXOSPHERE_LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Setup basic configuration with clean formatting
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Log that we're using default configuration
    logger = logging.getLogger(__name__)
    logger.debug(f"ExosphereHost: Using default logging configuration (level: {log_level_name})")


class Runtime:
    """
    Runtime for distributed execution of Exosphere nodes.

    The `Runtime` class manages the lifecycle and execution of a set of `BaseNode` subclasses
    in a distributed environment. It handles node registration, state polling, execution,
    and communication with a remote state manager service.

    Key Features:
        - Registers node schemas and runtime metadata with the state manager.
        - Polls for new states to process and enqueues them for execution.
        - Spawns worker tasks to execute node logic asynchronously.
        - Notifies the state manager of successful or failed executions.
        - Handles configuration via constructor arguments or environment variables.

    Args:
        namespace (str): Namespace for this runtime instance.
        name (str): Name of this runtime instance.
        nodes (List[type[BaseNode]]): List of node classes to register and execute.
        state_manager_uri (str | None, optional): URI of the state manager service.
            If not provided, will use the EXOSPHERE_STATE_MANAGER_URI environment variable.
        key (str | None, optional): API key for authentication.
            If not provided, will use the EXOSPHERE_API_KEY environment variable.
        batch_size (int, optional): Number of states to fetch per poll. Defaults to 16.
        workers (int, optional): Number of concurrent worker tasks. Defaults to 4.
        state_manage_version (str, optional): State manager API version. Defaults to "v0".
        poll_interval (int, optional): Seconds between polling for new states. Defaults to 1.

    Raises:
        ValueError: If configuration is invalid (e.g., missing URI or key, batch_size/workers < 1).
        ValidationError: If node classes are invalid or duplicate.

    Usage:
        runtime = Runtime(namespace="myspace", name="myruntime", nodes=[MyNode])
        runtime.start()
    """

    def __init__(self, namespace: str, name: str, nodes: List[type[BaseNode]], state_manager_uri: str | None = None, key: str | None = None, batch_size: int = 16, workers: int = 4, state_manage_version: str = "v0", poll_interval: int = 1):

        _setup_default_logging()

        self._name = name
        self._namespace = namespace
        self._key = key
        self._batch_size = batch_size
        self._state_queue = Queue(maxsize=2*batch_size)
        self._workers = workers
        self._nodes = nodes
        self._node_names = [node.__name__ for node in nodes]
        self._state_manager_uri = state_manager_uri
        self._state_manager_version = state_manage_version
        self._poll_interval = poll_interval
        self._node_mapping = {
            node.__name__: node for node in nodes
        }

        self._set_config_from_env()
        self._validate_runtime()
        self._validate_nodes()

    def _set_config_from_env(self):
        """
        Set configuration from environment variables if not provided.
        """
        if self._state_manager_uri is None:
            logger.debug("State manager URI not provided, falling back to environment variable EXOSPHERE_STATE_MANAGER_URI")
            self._state_manager_uri = os.environ.get("EXOSPHERE_STATE_MANAGER_URI")
        if self._key is None:
            logger.debug("API key not provided, falling back to environment variable EXOSPHERE_API_KEY")
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
        """
        Construct the endpoint URL for enqueueing states.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/enqueue"
    
    def _get_executed_endpoint(self, state_id: str):
        """
        Construct the endpoint URL for notifying executed states.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/{state_id}/executed"
    
    def _get_errored_endpoint(self, state_id: str):
        """
        Construct the endpoint URL for notifying errored states.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/{state_id}/errored"
    
    def _get_register_endpoint(self):
        """
        Construct the endpoint URL for registering nodes with the runtime.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/nodes/"
    
    def _get_secrets_endpoint(self, state_id: str):
        """
        Construct the endpoint URL for getting secrets.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/state/{state_id}/secrets"
    
    def _get_prune_endpoint(self, state_id: str):
        """
        Construct the endpoint URL for pruning a state.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/state/{state_id}/prune"
    
    def _get_requeue_after_endpoint(self, state_id: str):
        """
        Construct the endpoint URL for requeuing a state after a timedelta.
        """
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/state/{state_id}/re-enqueue-after"

    async def _register(self):
        """
        Register node schemas and runtime metadata with the state manager.

        Raises:
            RuntimeError: If registration fails.
        """
        logger.info(f"Registering nodes: {[f"{self._namespace}/{node.__name__}" for node in self._nodes]}")
        async with ClientSession() as session:
            endpoint = self._get_register_endpoint()
            body = {
                "runtime_name": self._name,
                "runtime_namespace": self._namespace,
                "nodes": [
                    {
                        "name": node.__name__,
                        "namespace": self._namespace,
                        "inputs_schema": node.Inputs.model_json_schema(),
                        "outputs_schema": node.Outputs.model_json_schema(),
                        "secrets": [
                            secret_name for secret_name in node.Secrets.model_fields.keys()
                        ]
                    } for node in self._nodes
                ]
            }
            headers = {"x-api-key": self._key}
            
            async with session.put(endpoint, json=body, headers=headers) as response: # type: ignore
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to register nodes: {res}")
                    raise RuntimeError(f"Failed to register nodes: {res}")
                
                logger.info(f"Registered nodes: {[f"{self._namespace}/{node.__name__}" for node in self._nodes]}")
                return res

    async def _enqueue_call(self):
        """
        Request a batch of states to process from the state manager.

        Returns:
            dict: Response from the state manager containing states to process.
        """
        async with ClientSession() as session:
            endpoint = self._get_enque_endpoint()
            body = {"nodes": self._node_names, "batch_size": self._batch_size}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response: # type: ignore
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to enqueue states: {res}")
                    raise RuntimeError(f"Failed to enqueue states: {res}")
                
                return res

    async def _enqueue(self):
        """
        Poll the state manager for new states and enqueue them for processing.

        This runs continuously, polling at the configured interval.
        """
        while True:
            try:
                if self._state_queue.qsize() < self._batch_size: 
                    data = await self._enqueue_call()
                    for state in data.get("states", []):
                        await self._state_queue.put(state)
                    logger.info(f"Enqueued states: {len(data.get('states', []))}")
            except Exception as e:
                logger.error(f"Error enqueuing states: {e}")
                await sleep(self._poll_interval * 2)
                continue

            await sleep(self._poll_interval)

    async def _notify_executed(self, state_id: str, outputs: List[BaseNode.Outputs]):
        """
        Notify the state manager that a state was executed successfully.

        Args:
            state_id (str): The ID of the executed state.
            outputs (List[BaseNode.Outputs]): Outputs from the node execution.
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
        Notify the state manager that a state execution failed.

        Args:
            state_id (str): The ID of the errored state.
            error (str): The error message.
        """
        async with ClientSession() as session:
            endpoint = self._get_errored_endpoint(state_id)
            body = {"error": error}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response: # type: ignore
                res =  await response.json()

                if response.status != 200:
                    logger.error(f"Failed to notify errored state {state_id}: {res}")


    async def _get_secrets(self, state_id: str) -> Dict[str, str]:
        """
        Get secrets for a state.
        """
        async with ClientSession() as session:
            endpoint = self._get_secrets_endpoint(state_id)
            headers = {"x-api-key": self._key}

            async with session.get(endpoint, headers=headers) as response: # type: ignore
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to get secrets for state {state_id}: {res}")
                    return {}
                
                if "secrets" in res:
                    return res["secrets"]
                else:
                    logger.error(f"'secrets' not found in response for state {state_id}")
                    return {}

    def _validate_nodes(self):
        """
        Validate that all provided nodes are valid BaseNode subclasses.

        Args:
            nodes (List[type[BaseNode]]): List of node classes to validate.

        Returns:
            List[type[BaseNode]]: The validated list of node classes.

        Raises:
            ValidationError: If any node is invalid or duplicate class names are found.
        """
        errors = []

        for node in self._nodes:
            if not issubclass(node, BaseNode):
                errors.append(f"{node.__name__} does not inherit from exospherehost.BaseNode")
            if not hasattr(node, "Inputs"):
                errors.append(f"{node.__name__} does not have an Inputs class")
            if not hasattr(node, "Outputs"):
                errors.append(f"{node.__name__} does not have an Outputs class")
            inputs_is_basemodel = hasattr(node, "Inputs") and issubclass(node.Inputs, BaseModel)
            if not inputs_is_basemodel:
                errors.append(f"{node.__name__} does not have an Inputs class that inherits from pydantic.BaseModel")
            outputs_is_basemodel = hasattr(node, "Outputs") and issubclass(node.Outputs, BaseModel)
            if not outputs_is_basemodel:
                errors.append(f"{node.__name__} does not have an Outputs class that inherits from pydantic.BaseModel")
            if not hasattr(node, "Secrets"):
                errors.append(f"{node.__name__} does not have an Secrets class")
            secrets_is_basemodel = hasattr(node, "Secrets") and issubclass(node.Secrets, BaseModel)
            if not secrets_is_basemodel:
                errors.append(f"{node.__name__} does not have an Secrets class that inherits from pydantic.BaseModel")

            # check all data objects are strings
            if inputs_is_basemodel:
                for field_name, field_info in node.Inputs.model_fields.items():
                    if field_info.annotation is not str:
                        errors.append(f"{node.__name__}.Inputs field '{field_name}' must be of type str, got {field_info.annotation}")
            if outputs_is_basemodel:
                for field_name, field_info in node.Outputs.model_fields.items():
                    if field_info.annotation is not str:
                        errors.append(f"{node.__name__}.Outputs field '{field_name}' must be of type str, got {field_info.annotation}")
            if secrets_is_basemodel:
                for field_name, field_info in node.Secrets.model_fields.items():
                    if field_info.annotation is not str:
                        errors.append(f"{node.__name__}.Secrets field '{field_name}' must be of type str, got {field_info.annotation}")
        
        # Find nodes with the same __class__.__name__
        class_names = [node.__name__ for node in self._nodes]
        duplicate_class_names = [name for name in set(class_names) if class_names.count(name) > 1]
        if duplicate_class_names:
            errors.append(f"Duplicate node class names found: {duplicate_class_names}")

        if len(errors) > 0:
            raise ValueError("Following errors while validating nodes: " + "\n".join(errors))
        
    def _need_secrets(self, node: type[BaseNode]) -> bool:
        """
        Check if the node needs secrets.
        """
        return len(node.Secrets.model_fields.keys()) > 0
        
    async def _worker(self, idx: int):
        """
        Worker task that processes states from the queue.

        Continuously fetches states from the queue, executes the corresponding node,
        and notifies the state manager of the result.
        """
        logger.info(f"Starting worker thread {idx} for nodes: {[f"{self._namespace}/{node.__name__}" for node in self._nodes]}")

        while True:
            state = await self._state_queue.get()
            node = None

            try:
                node = self._node_mapping[state["node_name"]]
                logger.info(f"Executing state {state['state_id']} for node {node.__name__}")

                secrets = {}
                if self._need_secrets(node):
                    secrets = await self._get_secrets(state["state_id"])
                    logger.info(f"Got secrets for state {state['state_id']} for node {node.__name__}")

                outputs = await node()._execute(node.Inputs(**state["inputs"]), node.Secrets(**secrets))
                logger.info(f"Got outputs for state {state['state_id']} for node {node.__name__}")
                
                if outputs is None:
                    outputs = []

                if not isinstance(outputs, list):
                    outputs = [outputs]

                await self._notify_executed(state["state_id"], outputs)
                logger.info(f"Notified executed state {state['state_id']} for node {node.__name__ if node else "unknown"}")
            
            except PruneSignal as prune_signal:
                logger.info(f"Pruning state {state['state_id']} for node {node.__name__ if node else "unknown"}")
                await prune_signal.send(self._get_prune_endpoint(state["state_id"]), self._key) # type: ignore
                logger.info(f"Pruned state {state['state_id']} for node {node.__name__ if node else "unknown"}")
            
            except ReQueueAfterSignal as requeue_signal:
                logger.info(f"Requeuing state {state['state_id']} for node {node.__name__ if node else "unknown"} after {requeue_signal.delay}")
                await requeue_signal.send(self._get_requeue_after_endpoint(state["state_id"]), self._key) # type: ignore
                logger.info(f"Requeued state {state['state_id']} for node {node.__name__ if node else "unknown"} after {requeue_signal.delay}")
                
            except Exception as e:
                logger.error(f"Error executing state {state['state_id']} for node {node.__name__ if node else "unknown"}: {e}")
                logger.error(traceback.format_exc())

                await self._notify_errored(state["state_id"], str(e))
                logger.info(f"Notified errored state {state['state_id']} for node {node.__name__ if node else "unknown"}")

            self._state_queue.task_done() # type: ignore

    async def _start(self):
        """
        Start the runtime event loop.

        Registers nodes, starts the polling and worker tasks, and runs until stopped.

        Raises:
            RuntimeError: If the runtime is not connected (no nodes registered).
        """
        await self._register()
        
        poller = asyncio.create_task(self._enqueue())
        worker_tasks = [asyncio.create_task(self._worker(idx)) for idx in range(self._workers)]

        await asyncio.gather(poller, *worker_tasks)

    def start(self):
        """
        Start the runtime in the current or a new asyncio event loop.

        If called from within an existing event loop, returns a task for the runtime.
        Otherwise, runs the runtime until completion.

        Returns:
            asyncio.Task | None: The runtime task if running in an existing event loop, else None.
        """
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(self._start())
        except RuntimeError:
            asyncio.run(self._start())
