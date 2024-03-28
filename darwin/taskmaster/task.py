from darwin.sampling.models import Models


class SampleTask:
    def __init__(self, prompt: str = "", model: Models = Models.dsc67) -> None:
        self.type = 0
        self.prompt = prompt
        self.model = model

