from darwin import *

spec = open("myspec", "r")

config = OllamaClientConfig(
    n_samplers=24,
    samplers={"deepseek-coder:6.7b-instruct": 0.5, "gemma:7b": 0.5},
    n_evaluators=10,
    n_post_processors=5,
    post_processors={"deepseek-coder:6.7b-instruct": 0.5, "gemma:7b": 0.5} | None = None,
)

client = OllamaClient(
    ollama_addresses=["http://localhost:11434", "www.myserver.com"], config=config
)

client.start(spec.read(), evolve_function="priority", eval_function="evaluate")

