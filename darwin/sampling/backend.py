from abc import ABC, abstractmethod


class Backend(ABC):
    @abstractmethod
    def prompt(self, prompt: str) -> str:
        pass
