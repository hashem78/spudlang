from enum import Enum


class StageThreeTokenType(str, Enum):
    IDENTIFIER = "identifier"
    NEW_LINE = "\n"
    FALSE = "false"
    TRUE = "true"
    IF = "if"
    FOR = "for"
    WHILE = "while"
    OR = "or"
    AND = "and"
    IN = "in"
