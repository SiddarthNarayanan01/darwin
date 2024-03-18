import requests
import json
from darwin.sampling.backend import Backend
from darwin.sampling.models import Models


class OllamaBackend(Backend):
    def __init__(self, server_address: str, model_name: Models) -> None:
        super().__init__()
        self.backend = "ollama"
        self.server_address = server_address
        match model_name:
            case Models.DEEPSEEK_MATH:
                self.model_name = "t1c/deepseek-math-7b-rl:latest"
            case Models.DEEPSEEK_CODER:
                self.model_name = "deepseek-coder:6.7b-instruct"
            case Models.STARCODER:
                self.model_name = "starcoder:15b"
            case Models.GEMMA:
                self.model_name = "gemma:7b"
            case _:
                raise ValueError(
                    f"Please provide a valid Model type, provided {model_name.name}"
                )

    def prompt(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "model": self.model_name,
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
