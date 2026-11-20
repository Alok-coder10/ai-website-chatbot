from abc import ABC, abstractmethod
from typing import Any

class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool.
        """
        raise NotImplementedError