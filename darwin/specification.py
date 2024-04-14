import ast

from darwin.configuration import ParseConfig


def parse_spec(file_name: str, config: ParseConfig) -> tuple[str]:
    contents = ""
    with open(file_name, "r") as f:
        contents = f.read()

    tree = ast.parse(contents)

    evolved_function = ""
    solve_function = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == config.evolved_function_name:
                evolved_function = ast.unparse(node)
            elif node.name == config.solver_function_name:
                solve_function = ast.unparse(node)

    return (evolved_function, solve_function)
