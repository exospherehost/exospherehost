from abc import ABC, abstractmethod
from typing import Optional

class BaseNode(ABC):

    def __init__(self, unique_name: Optional[str] = None):
        self.unique_name: Optional[str] = unique_name

    def get_unique_name(self) -> str:
        if self.unique_name is not None:
            return self.unique_name
        return self.__class__.__name__
        

class Foo1(BaseNode):

    def run(self):
        print(self.get_unique_name())


obj = Foo1()
print(obj.get_unique_name())
print(isinstance(obj, BaseNode))