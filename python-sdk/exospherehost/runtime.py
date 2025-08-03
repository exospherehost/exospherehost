import asyncio
from asyncio import Queue, sleep
from typing import Any, List
from .node.BaseNode import BaseNode
from aiohttp import ClientSession
from logging import getLogger

logger = getLogger(__name__)

class Runtime:

    def __init__(self, namespace: str, state_manager_uri: str, key: str, batch_size: int = 16, workers=4, state_manage_version: str = "v0", poll_interval: int = 1):
        self._namespace = namespace
        self._key = key
        self._batch_size = batch_size
        self._connected = False
        self._state_queue = Queue(maxsize=2*batch_size)
        self._workers = workers
        self._nodes = []
        self._node_names = []
        self._state_manager_uri = state_manager_uri
        self._state_manager_version = state_manage_version
        self._poll_interval = poll_interval
        self._node_mapping = {}

        if batch_size < 1:
            raise ValueError("Batch size should be at least 1")
        if workers < 1:
            raise ValueError("Workers should be at least 1")

    def _get_enque_endpoint(self):
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/enqueue"
    
    def _get_executed_endpoint(self, state_id: str):
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/{state_id}/executed"
    
    def _get_errored_endpoint(self, state_id: str):
        return f"{self._state_manager_uri}/{str(self._state_manager_version)}/namespace/{self._namespace}/states/{state_id}/errored"

    def connect(self, nodes: List[BaseNode]):
        self._nodes = self._validate_nodes(nodes)
        self._node_names = [node.get_unique_name() for node in nodes]
        self._node_mapping = {node.get_unique_name(): node for node in self._nodes}
        self._connected = True

    async def _enqueue_call(self):
        async with ClientSession() as session:
            endpoint = self._get_enque_endpoint()
            body = {"nodes": self._node_names, "batch_size": self._batch_size}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response:
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to enqueue states: {res}")
                
                return res

    async def _enqueue(self):
        while True:
            try:
                if self._state_queue.qsize() < self._batch_size: 
                    data = await self._enqueue_call()
                    for state in data["states"]:
                        await self._state_queue.put(state)
            except Exception as e:
                logger.error(f"Error enqueuing states: {e}")
                
            await sleep(self._poll_interval)

    async def _notify_executed(self, state_id: str, outputs: List[dict[str, Any]]):
        async with ClientSession() as session:
            endpoint = self._get_executed_endpoint(state_id)
            body = {"outputs": outputs}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response:
                res = await response.json()

                if response.status != 200:
                    logger.error(f"Failed to notify executed state {state_id}: {res}")
      
    async def _notify_errored(self, state_id: str, error: str):
        async with ClientSession() as session:
            endpoint = self._get_errored_endpoint(state_id)
            body = {"error": error}
            headers = {"x-api-key": self._key}

            async with session.post(endpoint, json=body, headers=headers) as response:
                res =  await response.json()

                if response.status != 200:
                    logger.error(f"Failed to notify errored state {state_id}: {res}")

    def _validate_nodes(self, nodes: List[BaseNode]):
        invalid_nodes = []

        for node in nodes:
            if not isinstance(node, BaseNode):
                invalid_nodes.append(f"{node.__class__.__name__}")

        if invalid_nodes:
            raise ValueError(f"Following nodes do not inherit from exospherehost.node.BaseNode: {invalid_nodes}")
        
        return nodes

    async def _worker(self):
        while True:
            state = await self._state_queue.get()

            try:
                node = self._node_mapping[state["node_name"]]
                outputs = await node.execute(state["inputs"]) # type: ignore

                if outputs is None:
                    outputs = []

                if isinstance(outputs, dict):
                    outputs = [outputs]

                await self._notify_executed(state["state_id"], outputs)
                
            except Exception as e:
                await self._notify_errored(state["state_id"], str(e))

            self._state_queue.task_done() # type: ignore

    async def _start(self):
        if not self._connected:
            raise RuntimeError("Runtime not connected, you need to call Runtime.connect() before calling Runtime.start()")
        
        poller = asyncio.create_task(self._enqueue())
        worker_tasks = [asyncio.create_task(self._worker()) for _ in range(self._workers)]

        await asyncio.gather(poller, *worker_tasks)

    def start(self):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(self._start())
        except RuntimeError:
            asyncio.run(self._start())
