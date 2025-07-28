from asyncio import Queue
from typing import List, TypeVar
from .node import BaseNode

T = TypeVar('T')


class Runtime:

    def __init__(self, namespace: str, state_manager_uri: str, batch_size: int = 16):
        self._namespace = namespace
        self._state_manager_uri = state_manager_uri
        self._batch_size = batch_size
        self._connected = False
        self._state_queue = Queue(maxsize=2*batch_size)
        self._nodes: List[BaseNode] = []

    async def connect(self, nodes: List[BaseNode]):
        self._validate_nodes(nodes)
        self._nodes = nodes

    async def _enqueue(self, batch_size: int):
        pass

    def _validate_nodes(self, nodes: List[BaseNode]):

        invalid_nodes = []

        for node in nodes:
            if not isinstance(node, BaseNode):
                invalid_nodes.append(f"{node.__class__.__name__}")

        if invalid_nodes:
            raise ValueError(f"Following nodes do not inherit from exospherehost.node.BaseNode: {invalid_nodes}")

        return nodes

    async def start(self):
        pass