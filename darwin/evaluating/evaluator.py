import asyncio
import functools


class Evaluator:
    def __init__(self) -> None:
        pass

    async def eval(self, code: str, inputs: tuple, function: str) -> int:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            functools.partial(
                self.__evaluate, code=code, inputs=inputs, function=function
            ),
        )

    def __evaluate(self, code: str, inputs: tuple, function: str) -> int:
        global_dict = globals()
        exec(code, global_dict)
        score = eval(f"{function}{inputs}", global_dict)
        return score
