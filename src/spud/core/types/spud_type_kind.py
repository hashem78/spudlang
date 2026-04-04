from enum import Enum


class SpudTypeKind(str, Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    UNIT = "unit"
    LIST = "list"
    FUNCTION = "function"
