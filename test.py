from lib.sampling.models import Models
from lib.sampling.sampler import Sampler


sampler = Sampler(
    backend="llamacpp",
    model_name=Models.DEEPSEEK_MATH,
    model_weights_path="./model_weights/deepseek-coder-6.7b-instruct.Q5_K_M.gguf",
)

print(
    sampler.prompt(
        "What is 16 choose 2 and what is a quick mathematical trick that can be used to solve this?"
    )
)
