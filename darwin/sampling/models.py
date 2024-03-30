from enum import Enum


class ModelType(Enum):
    dsc67 = "deepseek-coder:6.7b-instruct"
    dsmath = "t1c/deepseek-math-7b-rl:latest"
    gemma = "gemma:7b"
