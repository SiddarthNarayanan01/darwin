import json
from lib.sampling.models import Models
from lib.sampling.sampler import Sampler
from threading import Thread
import requests
import time
import multiprocessing


sampler = Sampler(
    backend="llamacpp",
    model_name=Models.DEEPSEEK_MATH,
    model_weights_path="./model_weights/deepseek-math-7b-rl.Q8_0.gguf",
)

prompt = r"""
Hello! Who are you?
"""


# def process(prompt):
#     print(time.time())
#     data = {"prompt": prompt, "n_predicts": 100}
#     r = requests.post("http://localhost:8080/completion", data=json.dumps(data))
#     print(r.json()["content"])
#     print("\n" * 10)
#
#
# if __name__ == "__main__":
#     pool = multiprocessing.Pool(processes=8)
#     pool.map(process, [prompt for _ in range(8)])

def sample(sampler, prompt, callback):
    sampler.sample(prompt, callback)

threads = [
    Thread(target=sample, args=(sampler, prompt, print)),
    Thread(target=sample, args=(sampler, prompt, print)),
    Thread(target=sample, args=(sampler, prompt, print)),
    Thread(target=sample, args=(sampler, prompt, print)),
]

for i, t in enumerate(threads):
    t.start()
    t.join()
