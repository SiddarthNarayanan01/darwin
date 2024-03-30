from darwin.sampling.models import ModelType


class SampleTask:
    def __init__(self, prompt: str = "", model: ModelType = ModelType.dsc67) -> None:
        self.type = 0
        self.prompt = prompt
        self.model = model

