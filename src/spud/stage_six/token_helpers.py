from spud.core.position import Position
from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_six.stage_six_token import StageSixToken
from spud.stage_six.stage_six_token_type import StageSixTokenType

OPERATOR_TYPES = {
    StageFourTokenType.PLUS,
    StageFourTokenType.MINUS,
    StageFourTokenType.MULTIPLY,
    StageFourTokenType.DIVIDE,
    StageFourTokenType.MODULO,
    StageFourTokenType.EQUALS,
    StageFourTokenType.NOT_EQUALS,
    StageFourTokenType.LESS_THAN,
    StageFourTokenType.GREATER_THAN,
    StageFourTokenType.LESS_THAN_OR_EQUAL,
    StageFourTokenType.GREATER_THAN_OR_EQUAL,
    StageFourTokenType.LOGICAL_AND,
    StageFourTokenType.LOGICAL_OR,
}


def _make_node(
    tokens: list[StageFourToken],
    children: list[StageSixToken] | None = None,
) -> StageSixToken:
    """Create an unclassified node. Type is EXPRESSION as placeholder."""
    return StageSixToken(
        token_type=StageSixTokenType.EXPRESSION,
        position=tokens[0].position if tokens else children[0].position if children else Position(line=0, column=0),
        tokens=tokens,
        children=children or [],
    )


def _has_token(tokens: list[StageFourToken], token_type: StageFourTokenType) -> bool:
    return any(t.token_type == token_type for t in tokens)


def _find_token(tokens: list[StageFourToken], token_type: StageFourTokenType) -> int | None:
    for i, t in enumerate(tokens):
        if t.token_type == token_type:
            return i
    return None


def _has_adjacent(tokens: list[StageFourToken], first: StageFourTokenType, second: StageFourTokenType) -> bool:
    for i in range(len(tokens) - 1):
        if tokens[i].token_type == first and tokens[i + 1].token_type == second:
            return True
    return False
