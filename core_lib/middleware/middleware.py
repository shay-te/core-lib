from abc import abstractmethod, ABC
from typing import Any, Callable


class Middleware(ABC):
    @abstractmethod
    def handle(self, context: Any) -> None:
        pass