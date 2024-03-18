from typing import Any, Callable, Literal
from darwin.sampling.backends.llamacpp import LlamaCPPBackend
from darwin.sampling.backends.ollama import OllamaBackend
from darwin.sampling.models import Models


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
                if "ollama_server_address" not in kwargs:
                    raise ValueError(
                        "Using OllamaBackend but not server address was given. Please supply the ollama_server_address keyword argument"
                    )
                self.backend = OllamaBackend(
                    server_address=kwargs["ollama_server_address"],
                    model_name=model_name,
                )
            case "groq":
                raise NotImplementedError()
            case _:
                raise ValueError(
                    "Backend must be one of ['llamacpp', 'groq', 'ollama']"
                )
        self.prompt_supplement = prompt_supplement

    def sample(self, prompt: str) -> str:
        return self.backend.prompt(f"{self.prompt_supplement}\n\n{prompt}")
