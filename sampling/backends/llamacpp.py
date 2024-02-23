import os
from pathlib import Path
from llama_cpp import Llama
from sampling.backend import Backend
from sampling.models import Models


class LlamaCPPBackend(Backend):
    def __init__(self, model_path: str, model_name: Models) -> None:
        super().__init__()
        self.backend = "llamacpp"
        if "MODEL_WEIGHTS_DIR" not in os.environ:
            raise ValueError(
                "Please set the MODEL_WEIGHTS_DIR environment variable to point to the folder containing the gguf model weights"
            )
        if Path(model_path).is_file():
            self.llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=4096)
        else:
            raise FileNotFoundError(
                f"ERROR: {model_name.name} not found! Could not find {model_path}.gguf"
            )

    def prompt(self, prompt: str) -> str:
        try:
            return self.llm(prompt, echo=False)["choices"][0]["text"]
        except Exception:
            # TODO: Get logging sorted out
            return ""
