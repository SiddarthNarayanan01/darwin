import re

class RegExParser:
    @staticmethod
    def parse(code: str) -> str:
        parsed = re.search(r"(?<!`)`{3}(?:(?!`)[^`]|\n|\r|\`(?!`))*?`{3}(?!`)", code)
        if parsed:
            try:
                parsed = parsed.group(0)
                parsed = parsed[parsed.index("def") : parsed.rfind("```")].strip()
                return parsed
            except:
                return code
        return code

