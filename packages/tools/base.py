from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Base class for every tool in Noticode.
    """

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool.
        """

    @abstractmethod
    def validate(self, **kwargs: Any) -> bool:
        """
        Validate input before execution.
        """
