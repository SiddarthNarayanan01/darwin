import ast
from darwin.configuration import SpecParseConfig


def parse_spec(spec: str, config: SpecParseConfig) -> tuple[str, str]:
    tree = ast.parse(spec)

    evolved_function = ""
    solve_function = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == config.evolved_function_name:
                evolved_function = ast.unparse(node)
            elif node.name == config.solver_function_name:
                solve_function = ast.unparse(node)

    return (evolved_function, solve_function)
