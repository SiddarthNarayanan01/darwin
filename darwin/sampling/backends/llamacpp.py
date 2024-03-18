from pathlib import Path
from llama_cpp import Llama
from darwin.sampling.backend import Backend
from darwin.sampling.models import Models


class LlamaCPPBackend(Backend):
    def __init__(self, model_weights_path: str, model_name: Models) -> None:
        super().__init__()
        self.backend = "llamacpp"
        if Path(model_weights_path).is_file():
            self.llm = Llama(
                model_path=model_weights_path,
                n_gpu_layers=-1,
                n_ctx=4096,
                chat_format="llama-2",
                # TODO: Configuration option
                n_threads=16,
            )
        else:
            raise FileNotFoundError(
                f"ERROR: {model_name.name} not found! Could not find {model_weights_path}"
            )

    def prompt(self, prompt: str) -> str:
        try:
            return str(
                self.llm.create_chat_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that's knowledgeable in python coding and mathematics.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=512
                )["choices"][0]["message"]["content"],
            )
            # return self.llm(prompt, echo=False, max_tokens=None)["choices"][0]["text"]
        except Exception:
            # TODO: Get logging sorted out
            return ""
