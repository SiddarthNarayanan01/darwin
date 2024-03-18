import ast


def validate_syntax(code: str) -> bool:
    try:
        ast.parse(code)
    except:
        return False
    return True
