from abc import ABC, abstractmethod
from typing import Optional, Any, List


class BaseNode(ABC):

    def __init__(self, unique_name: Optional[str] = None):
        self.unique_name: Optional[str] = unique_name

    @abstractmethod
    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any] | List[dict[str, Any]]:
        pass

    def get_unique_name(self) -> str:
        if self.unique_name is not None:
            return self.unique_name
        return self.__class__.__name__