from enum import Enum

from pydantic import BaseModel

from spud.stage_five.stage_five_token_type import StageFiveTokenType


class Associativity(str, Enum):
    LEFT = "left"
    NONE = "none"


class OperatorKind(str, Enum):
    BINARY = "binary"
    UNARY_PREFIX = "unary_prefix"


class OperatorInfo(BaseModel, frozen=True):
    token: StageFiveTokenType
    precedence: int
    kind: OperatorKind = OperatorKind.BINARY
    associativity: Associativity = Associativity.LEFT
    commutative: bool = True
