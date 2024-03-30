from abc import ABC, abstractmethod
from enum import Enum

class Backend(ABC):
    @abstractmethod
    async def prompt(self, prompt: str) -> str:
        pass


class BackendType(Enum):
    ollama = 0
    groq = 1
    llamacpp = 2

