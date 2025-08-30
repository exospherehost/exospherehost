from typing import Any
from aiohttp import ClientSession
from datetime import timedelta

class PruneSignal(Exception):
    """
    Exception used to signal that a prune operation should be performed.

    Args:
        data (dict[str, Any], optional): Additional data to include with the signal. Defaults to {}.

    Note:
        Do not catch this Exception, let it bubble up to Runtime for handling at StateManager.
    """
    def __init__(self, data: dict[str, Any] = {}):
        self.data = data
        super().__init__(f"Prune signal received with data: {data} \n NOTE: Do not catch this Exception, let it bubble up to Runtime for handling at StateManager")

    async def send(self, endpoint: str, key: str):
        """
        Sends the prune signal to the specified endpoint.

        Args:
            endpoint (str): The URL to send the signal to.
            key (str): The API key to include in the request headers.

        Raises:
            Exception: If the HTTP request fails (status code != 200).
        """
        async with ClientSession() as session:
            async with session.post(endpoint, json=self.data, headers={"x-api-key": key}) as response:
                if response.status != 200:
                    raise Exception(f"Failed to send prune signal to {endpoint}")
                

class ReQueueAfterSignal(Exception):
    """
    Exception used to signal that a requeue operation should be performed after a specified timedelta.

    Args:
        timedelta (timedelta): The amount of time to wait before requeuing.

    Note:
        Do not catch this Exception, let it bubble up to Runtime for handling at StateManager.
    """
    def __init__(self, delay: timedelta):
        self.delay = delay

        if self.delay.total_seconds() <= 0:
            raise Exception("Delay must be greater than 0")

        super().__init__(f"ReQueueAfter signal received with timedelta: {timedelta} \n NOTE: Do not catch this Exception, let it bubble up to Runtime for handling at StateManager")

    async def send(self, endpoint: str, key: str):
        """
        Sends the requeue-after signal to the specified endpoint.

        Args:
            endpoint (str): The URL to send the signal to.
            key (str): The API key to include in the request headers.

        Raises:
            Exception: If the HTTP request fails (status code != 200).
        """
        body = {
            "enqueue_after": int(self.delay.total_seconds() * 1000)
        }
        async with ClientSession() as session:
            async with session.post(endpoint, json=body, headers={"x-api-key": key}) as response:
                if response.status != 200:
                    raise Exception(f"Failed to send requeue after signal to {endpoint}")
