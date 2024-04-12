import asyncio
from pathlib import Path
from llama_cpp import Llama
import functools
from darwin.sampling.backend import Backend
from darwin.sampling.models import ModelType


class LlamaCPPBackend(Backend):
    def __init__(self, model_weights_path: str, model: ModelType) -> None:
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
                f"ERROR: Could not find {model_weights_path}"
            )

    async def prompt(self, prompt: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            return str(
                (
                    await loop.run_in_executor(
                        None,
                        functools.partial(
                            self.llm.create_chat_completion,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant that's knowledgeable in python coding and mathematics. Be concise and only do what's asked of you directly.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.8,
                            top_p=0.4,
                            seed=-1,
                            max_tokens=1024,
                        ),
                    )
                )["choices"][0]["message"]["content"]
            )
        except Exception:
            # TODO: Get logging sorted out
            return ""
