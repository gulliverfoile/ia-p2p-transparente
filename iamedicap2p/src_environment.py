from abc import ABC, abstractmethod
from typing import Any, Tuple

class Environment(ABC):
    @abstractmethod
    def reset(self) -> Any:
        pass

    @abstractmethod
    def step(self, action: str) -> Tuple[Any, float, bool, dict]:
        pass

    @abstractmethod
    def get_state_repr(self, obs: Any) -> str:
        pass