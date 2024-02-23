from sampling.backend import Backend


class Sampler:
    def __init__(self, backend: Backend, prompt_supplement: str) -> None:
        self.backend = backend
        self.prompt_supplement = prompt_supplement

    def prompt(self, prompt: str) -> str:
        return self.backend.prompt(f"{self.prompt_supplement}\n\n{prompt}")
