from spud.stage_five.stage_five_token_type import StageFiveTokenType as T

KEYWORDS: frozenset[T] = frozenset(
    {
        T.IF,
        T.ELIF,
        T.ELSE,
        T.FOR,
        T.IN,
        T.WHILE,
        T.MATCH,
        T.TRUE,
        T.FALSE,
        T.OR,
        T.AND,
    }
)
