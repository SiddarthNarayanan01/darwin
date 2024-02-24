from pathlib import Path
from llama_cpp import Llama
from lib.sampling.backend import Backend
from lib.sampling.models import Models


class LlamaCPPBackend(Backend):
    def __init__(self, model_weights_path: str, model_name: Models) -> None:
        super().__init__()
        self.backend = "llamacpp"
        if Path(model_weights_path).is_file():
            self.llm = Llama(model_path=model_weights_path, n_gpu_layers=-1, n_ctx=4096)
        else:
            raise FileNotFoundError(
                f"ERROR: {model_name.name} not found! Could not find {model_weights_path}"
            )

    def prompt(self, prompt: str) -> str:
        try:
            return self.llm(prompt, echo=False)["choices"][0]["text"]
        except Exception:
            # TODO: Get logging sorted out
            return ""
