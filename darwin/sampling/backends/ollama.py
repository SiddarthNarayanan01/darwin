import json
import aiohttp

# import json
from darwin.sampling.backend import Backend
from darwin.sampling.models import ModelType


class OllamaBackend(Backend):
    def __init__(self, server_address: str, model: ModelType) -> None:
        super().__init__()
        self.server_address = server_address
        self.model = model.value

    async def prompt(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{self.server_address}/api/generate",
                data=json.dumps(data),
                headers=headers,
            ) as response:
                response = await response.json()
                result = response["response"]
                return result
