from lib.sampling.models import Models
from lib.sampling.sampler import Sampler


sampler = Sampler(
    backend="ollama",
    model_name=Models.DEEPSEEK_MATH,
    ollama_server_address="http://127.0.0.1:11434"
)

prompt = r"""
"""

sampler.sample(prompt, print)
