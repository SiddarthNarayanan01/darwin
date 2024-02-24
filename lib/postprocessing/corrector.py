from lib.sampling.sampler import Sampler
from lib.sampling.backend import Backend
from lib.postprocessing.parser import RegExParser



class Corrector(Sampler):
    def __init__(self, backend: Backend, prompt_supplement: str = "") -> None:
        if not prompt_supplement:
            prompt_supplement = """Correct any syntax errors that are present in this code.
            Do NOT change the intent of the code, simply fix syntactical issues and/or issues with numpy, itertools, and any other library,
            that may have been made. Once you are done fixing the code, simply output the fixed Python function in markdown format.
            Use markdown code blocks to separate the code from any explanations or commentary that you provide."""
        super().__init__(backend, prompt_supplement)

    def fix(self, sample: str) -> str:
        return RegExParser.parse(
            self.backend.prompt(f"{self.prompt_supplement}\n\n{sample}")
        )
