import requests
import json
from darwin.sampling.backend import Backend
from darwin.sampling.models import Models


class OllamaBackend(Backend):
    def __init__(self, server_address: str, model: Models) -> None:
        super().__init__()
        self.server_address = server_address
        self.model = model.value

    def prompt(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "model": self.model,
            "prompt": prompt,
        }
        try:
            response = requests.post(
                f"{self.server_address}/api/generate", headers=headers, data=json.dumps(data), timeout=10
            )
        except requests.exceptions.Timeout:
            print("Timeout Error: ollama did not respond within 10 seconds")
            return ""
            # TODO: Should be logging here

        try:
            responses = response.text.split("\n")[:-1]
            response = ""
            for r in responses:
                response += json.loads(r)["response"]
            return response
        except:
            print(f"Error parsing ollama response object. \nOllama: {response}")
            return ""
            # TODO: Should be logging here
