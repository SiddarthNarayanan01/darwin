from typing import Literal
from lib.sampling.backends.llamacpp import LlamaCPPBackend
from lib.sampling.models import Models


class Sampler:
    def __init__(
        self,
        backend: Literal["llamacpp", "groq", "ollama"],
        model_name: Models,
        prompt_supplement: str = "",
        **kwargs,
    ) -> None:
        match backend:
            case "llamacpp":
                if "model_weights_path" not in kwargs:
                    raise ValueError(
                        "Using LlamaCPPBackend but no model weights were given. Please supply the model_weights_path keyword argument"
                    )
                self.backend = LlamaCPPBackend(
                    model_weights_path=kwargs["model_weights_path"],
                    model_name=model_name,
                )
            case "ollama":
                raise NotImplementedError()
            case "groq":
                raise NotImplementedError()
            case _:
                raise ValueError(
                    "Backend must be one of ['llamacpp', 'groq', 'ollama']"
                )
        self.prompt_supplement = prompt_supplement

    def prompt(self, prompt: str) -> str:
        return self.backend.prompt(f"{self.prompt_supplement}\n\n{prompt}")
