from abc import abstractmethod, ABC
from typing import Any


class Middleware(ABC):
    @abstractmethod
    def handle(self, context: Any) -> None:
        pass