from darwin2.client.ollama import OllamaClient
from darwin2.configuration.ollama import OllamaConfig

config = OllamaConfig(
    samplers={"deepseek-coder:6.7b-instruct": 0.5, "llama3:8b": 0.5},
    n_samplers=6,
    correctors={"llama2:latest": 1},
    n_correctors=2,
    n_evaluators=10,
)

# To access endpoint on different computer, make sure to specify OLLAMA_HOST=IP:PORT
client = OllamaClient(endpoints=["http://localhost:11434/api/generate"], corrector_endpoints=["http://172.31.142.130:11434/api/generate", "http://172.31.133.234:11434/api/generate"], config=config)

with open("./sentence_specification.py", "r") as f:
    spec = f.read()

if __name__ == "__main__":
    client.start(
        spec,
        evolve_function_name="priority",
        solve_function_name="evaluate",
        inputs=(5, 3, 3),
    )
