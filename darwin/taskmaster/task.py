import json


class SampleTask:
    def __init__(self, prompt: str, island_id: int) -> None:
        self.step_id = 0
        self.prompt = prompt
        self.island_id = island_id

    def serialize(self):
        return json.dumps({"prompt": self.prompt, "island_id": self.island_id})


class PostProcessTask:
    def __init__(self, code: str, island_id: int):
        self.step_id = 1
        self.code = code
        self.island_id = island_id

    def serialize(self):
        return json.dumps({"code": self.code, "island_id": self.island_id})


class EvaluateTask:
    def __init__(
        self,
        code: str,
        island_id: int,
        specification: str,
        inputs: tuple,
        eval_function: str,
    ) -> None:
        self.code = code
        self.island_id = island_id
        self.specification = specification
        self.inputs = inputs
        self.eval_function = eval_function

    def serialize(self):
        return json.dumps(
            {
                "code": self.code,
                "island_id": self.island_id,
                "specification": self.specification,
                "inputs": self.inputs,
                "eval_function": self.eval_function,
            }
        )


class EvolveTask:
    def __init__(self, code: str, island_id: int) -> None:
        self.step_id = 2
        self.code = code
        self.island_id = island_id

    def serialize(self):
        return json.dumps({"code": self.code, "island_id": self.island_id})
