import json
import aiohttp

from darwin.sampling.backend import Backend
from darwin.sampling.models import ModelType


class OllamaBackend(Backend):
    def __init__(self, server_address: str, model: ModelType) -> None:
        super().__init__()
        self.server_address = server_address
        match model:
            case ModelType.deepseekcoder67:
                self.model = "deepseek-coder:6.7b"
            case ModelType.dsmath:
                self.model = "t1c/deepseek-math-7b-rl:latest"
            case ModelType.gemma:
                self.model = "gemma:7b"
            case ModelType.llama2:
                self.model = "llama2:7b-chat"
            case ModelType.codellama13b:
                self.model = "codellama:13b"
        self.model = model.value

    async def prompt(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"model": self.model, "prompt": prompt, "stream": False}
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{self.server_address}/api/generate",
                data=json.dumps(data),
                headers=headers,
            ) as response:
                response = await response.json()
                result = response["response"]
                return result


# TODO: make more efficient by not creating session one very request
