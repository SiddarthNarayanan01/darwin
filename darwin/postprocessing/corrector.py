from darwin.sampling.backend import BackendType
from darwin.sampling.models import ModelType
from darwin.sampling.sampler import Sampler
from darwin.postprocessing.parser import RegExParser


class Corrector(Sampler):
    def __init__(self, backend: BackendType, model_name: ModelType, **kwargs) -> None:
        if "prompt_supplement" not in kwargs:
            self.prompt_supplement = """Correct any syntax errors that are present in this code.
            Do NOT change the intent/underlying workings of the code. Simply fix syntactical issues and/or issues with numpy, itertools,
            and any other imported library, that may have been made. Once you are done fixing the code, simply output the fixed Python 
            function in markdown format. Use a markdown code block to separate the revised function from any explanations or commentary that you provide."""
            kwargs["prompt_supplement"] = self.prompt_supplement
        super().__init__(backend, model_name, **kwargs)

    async def fix(self, sample: str) -> str:
        return RegExParser.parse(
            await self.backend.prompt(f"{self.prompt_supplement}\n\n{sample}")
        )
