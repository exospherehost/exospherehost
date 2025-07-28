from asyncio import Queue
from typing import List, TypeVar

T = TypeVar('T')


class Runtime:

    def __init__(self, namespace: str, state_manager_uri: str, batch_size: int = 16):
        self._namespace = namespace
        self._state_manager_uri = state_manager_uri
        self._batch_size = batch_size
        self._connected = False
        self._state_queue = Queue(maxsize=2*batch_size)

    async def connect(self, nodes: List[T]):
        pass

    async def _enqueue(self, batch_size: int):
        pass

    def _validate_nodes(self):
        pass