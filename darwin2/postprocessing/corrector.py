from darwin2.sampling.backend import BackendType
from darwin2.sampling.models import ModelType
from darwin2.sampling.sampler import Sampler
from darwin2.postprocessing.parser import RegExParser


class Corrector(Sampler):
    def __init__(self, backend: BackendType, model_name: ModelType, **kwargs) -> None:
        if "prompt_supplement" not in kwargs:
            self.prompt_supplement = """Correct any syntax errors that are present in this code.
            Do NOT change the intent/underlying workings of the code. Simply fix syntactical issues 
            and output the raw function. Surround the function with a markdown code block."""
            kwargs["prompt_supplement"] = self.prompt_supplement
        super().__init__(backend, model_name, **kwargs)

    async def fix(self, sample: str) -> str:
        return RegExParser.parse(
            await self.backend.prompt(f"{self.prompt_supplement}\n\n{sample}")
        )
