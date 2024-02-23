from abc import ABC, abstractmethod


class Backend(ABC):
    @abstractmethod
    def prompt(self, prompt: str) -> str:
        pass

    @property
    def backend(self):
        pass

    @backend.getter
    def backend(self) -> str:
        return self._backend

    @backend.setter
    def backend(self, b):
        self._backend = b
