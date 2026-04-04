from enum import Enum


class ParseErrorKind(str, Enum):
    UNEXPECTED_END = "unexpected_end"
    UNEXPECTED_TOKEN = "unexpected_token"
