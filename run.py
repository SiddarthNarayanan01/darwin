from darwin2.client.ollama import OllamaClient
from darwin2.configuration.ollama import OllamaConfig

config = OllamaConfig(
    samplers={"deepseek-coder:6.7b-instruct": 1},
    n_samplers=10,
    n_evaluators=5,
)

# To access endpoint on different computer, make sure to specify OLLAMA_HOST=IP:PORT
client = OllamaClient(
    endpoints=["http://localhost:11434/api/generate"],
    config=config,
)

with open("./ramsey_spec.py", "r") as f:
    spec = f.read()

if __name__ == "__main__":
    client.start(
        spec,
        evolve_function_name="priority",
        solve_function_name="evaluate",
        inputs=(5, 5, 16),
        log_base_path=".",
    )
