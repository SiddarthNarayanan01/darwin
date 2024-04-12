import asyncio
import os

from llama_cpp import functools
from darwin.sampling.backend import Backend
from darwin.sampling.models import ModelType
from groq import Groq


class GroqBackend(Backend):
    def __init__(self, model: ModelType) -> None:
        super().__init__()
        self.backend = "groq"
        if "GROQ_API_KEY" not in os.environ:
            raise ValueError(
                "Specified Groq as backend but missing GROQ_API_KEY environment variable"
            )
        self.llm = Groq(api_key=os.environ["GROQ_API_KEY"])
        match model:
            case ModelType.gemma:
                self.model = "gemma-7b-it"
            case _:
                raise ValueError("Model provided not supported by Groq")

    async def prompt(self, prompt: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    self.llm.chat.completions.create,
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that's knowledgeable in python coding and mathematics. Be concise and only do what's asked of you directly.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                ),
            )
            return response.choices[0].message.content
        except:
            return ""
