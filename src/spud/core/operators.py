from spud.core.operator_info import Associativity, OperatorInfo, OperatorKind
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T

OPERATORS: list[OperatorInfo] = [
    OperatorInfo(token=T.LOGICAL_OR, precedence=1),
    OperatorInfo(token=T.LOGICAL_AND, precedence=2),
    OperatorInfo(token=T.EQUALS, precedence=3, associativity=Associativity.NONE),
    OperatorInfo(token=T.NOT_EQUALS, precedence=3, associativity=Associativity.NONE),
    OperatorInfo(token=T.LESS_THAN, precedence=3, associativity=Associativity.NONE),
    OperatorInfo(token=T.GREATER_THAN, precedence=3, associativity=Associativity.NONE),
    OperatorInfo(token=T.LESS_THAN_OR_EQUAL, precedence=3, associativity=Associativity.NONE),
    OperatorInfo(token=T.GREATER_THAN_OR_EQUAL, precedence=3, associativity=Associativity.NONE),
    OperatorInfo(token=T.PLUS, precedence=4),
    OperatorInfo(token=T.MINUS, precedence=4, commutative=False),
    OperatorInfo(token=T.MULTIPLY, precedence=5),
    OperatorInfo(token=T.DIVIDE, precedence=5, commutative=False),
    OperatorInfo(token=T.MODULO, precedence=5, commutative=False),
    OperatorInfo(token=T.MINUS, precedence=6, kind=OperatorKind.UNARY_PREFIX),
    OperatorInfo(token=T.PLUS, precedence=6, kind=OperatorKind.UNARY_PREFIX),
]
