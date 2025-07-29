import asyncio
from asyncio import Queue, sleep
import logging
from typing import Any, List
from .node import BaseNode
from aiohttp import ClientSession

class Runtime:

    def __init__(self, namespace: str, state_manager_uri: str, batch_size: int = 16, workers=4, state_manage_version: int = 0, poll_interval: int = 10):
        self._namespace = namespace
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

    async def connect(self, nodes: List[BaseNode]):
        self._nodes = self._validate_nodes(nodes)
        self._node_names = [node.get_unique_name() for node in nodes]
        self._node_mapping = {node.get_unique_name(): node for node in self._nodes}
        self._connected = True

    async def _enqueue_call(self):
        async with ClientSession() as session:
            async with session.post(self._get_enque_endpoint(), json={"nodes": self._node_names, "batch_size": self._batch_size}) as response:
                return await response.json()

    async def _enqueue(self):
        if self._state_queue.qsize() < self._batch_size: 
            data = await self._enqueue_call()
            for state in data["states"]:
                await self._state_queue.put(state)
        await sleep(self._poll_interval)

    async def _notify_executed(self, state_id: str, outputs: dict[str, Any]):
        async with ClientSession() as session:
            async with session.post(self._get_executed_endpoint(state_id), json={"outputs": outputs}) as response:
                return await response.json()
      
    async def _notify_errored(self, state_id: str, error: str):
        async with ClientSession() as session:
            async with session.post(self._get_errored_endpoint(state_id), json={"error": error}) as response:
                return await response.json()

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
                await self._notify_executed(state["id"], outputs)
            except Exception as e:
                await self._notify_errored(state["id"], str(e))

    async def start(self):
        if not self._connected:
            raise RuntimeError("Runtime not connected, you need to call Runtime.connect() before calling Runtime.start()")
        
        poller = asyncio.create_task(self._enqueue())
        worker_tasks = [asyncio.create_task(self._worker()) for _ in range(self._workers)]

        await asyncio.gather(poller, *worker_tasks)