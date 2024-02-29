from typing import Literal
from lib.sampling.models import Models
from lib.sampling.sampler import Sampler
from lib.postprocessing.parser import RegExParser


class Corrector(Sampler):
    def __init__(
        self,
        backend: Literal["llamacpp", "groq", "ollama"],
        model_name: Models,
        prompt_supplement: str = "",
    ) -> None:
        if not prompt_supplement:
            prompt_supplement = """Correct any syntax errors that are present in this code.
            Do NOT change the intent/underlying workings of the code. Simply fix syntactical issues and/or issues with numpy, itertools,
            and any other imported library, that may have been made. Once you are done fixing the code, simply output the fixed Python 
            function in markdown format. Use a markdown code block to separate the revised function from any explanations or commentary that you provide."""
        super().__init__(backend, model_name)

    def fix(self, sample: str) -> str:
        return RegExParser.parse(
            self.backend.prompt(f"{self.prompt_supplement}\n\n{sample}")
        )

