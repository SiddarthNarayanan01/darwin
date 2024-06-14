import ast
from multiprocessing.queues import Queue
from typing import Tuple, Any

from darwin2.evolving.samples import Sample


class Evaluator:
    def __init__(self) -> None:
        pass

    def eval(
        self,
        scores_queue: Queue,
        spec: str,
        sample: Sample,
        inputs: Tuple[Any, ...],
        function: str,
        base_function_name: str,
    ):
        spec = self.__reformat_spec(
            spec,
            sample.code,
            base_function_name,
        )
        global_dict = globals()
        try:
            exec(spec, global_dict)
            score = eval(f"{function}{inputs}", global_dict)
            scores_queue.put(Sample(sample.code, sample.island_id, score), block=False)
        except Exception as e:
            # print(e)
            scores_queue.put(Sample(sample.code, sample.island_id, 0), block=False)

    def __rename_function(self, sample: str, base_function_name: str):
        try:
            tree = ast.parse(sample)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    node.name = base_function_name

            return ast.unparse(tree)
        except:
            return sample

    def __reformat_spec(self, spec: str, sample: str, base_function_name: str):
        sample = self.__rename_function(sample, base_function_name)
        try:
            tree = ast.parse(spec)

            class FunctionRemover(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    if node.name == base_function_name:
                        return None
                    return node

            remover = FunctionRemover()
            removed_spec = ast.unparse(remover.visit(tree))
            removed_spec += f"\n{sample}"
            return removed_spec
        except:
            return spec
