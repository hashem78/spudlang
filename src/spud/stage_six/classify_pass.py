from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_six.stage_six_token import StageSixToken
from spud.stage_six.stage_six_token_type import StageSixTokenType
from spud.stage_six.token_helpers import OPERATOR_TYPES, _has_adjacent, _has_token


class ClassifyPass:
    """Assign expression types to all nodes in a decomposed tree.

    Walks the tree bottom-up and replaces the placeholder EXPRESSION
    type with the correct type based on each node's tokens. This is
    a pure pass — it never changes the tree structure, only the type
    label on each node.

    Classification rules are checked in priority order — first match
    wins. The priority is designed so that more specific patterns
    (single-token literals) are checked before broader ones (operators)::

        1. Empty tokens         → EXPRESSION (container node)
        2. Single STRING        → STRING_LITERAL
        3. Single RAW_STRING    → RAW_STRING_LITERAL
        4. Single TRUE/FALSE    → BOOLEAN_LITERAL
        5. Single all-digit ID  → NUMERIC_LITERAL
        6. Starts with FOR      → FOR_LOOP
        7. Starts with WHILE    → WHILE_LOOP
        8. Starts with IF       → IF_EXPR
        9. Starts with ELIF     → ELIF_EXPR
        10. Starts with ELSE    → ELSE_EXPR
        11. Starts with MATCH   → MATCH_EXPR
        12. Contains :=         → ASSIGNMENT
        13. Contains =>         → FUNCTION_DEF
        14. Has ident(          → FUNCTION_CALL
        15. Has operator (3+)   → BINARY_OP
        16. Fallback            → EXPRESSION
    """

    def process(self, node: StageSixToken) -> StageSixToken:
        """Classify a node and all its children recursively.

        Children are classified first (bottom-up), then the node itself.
        Returns a new node with the correct type — the original is not mutated.
        """
        children = [self.process(child) for child in node.children]
        token_type = self._determine_type(node.tokens)
        return StageSixToken(
            token_type=token_type,
            position=node.position,
            tokens=node.tokens,
            children=children,
        )

    def _determine_type(self, tokens: list[StageFourToken]) -> StageSixTokenType:
        """Determine the expression type from its tokens.

        Rules are checked in priority order — first match wins.
        """
        # No tokens — this is a structural container created by decomposition.
        if not tokens:
            return StageSixTokenType.EXPRESSION

        # Single-token expressions — check the token type directly.
        if len(tokens) == 1:
            match tokens[0].token_type:
                # Quoted string literal: "hello"
                case StageFourTokenType.STRING:
                    return StageSixTokenType.STRING_LITERAL
                # Backtick raw string: `hello`
                case StageFourTokenType.RAW_STRING:
                    return StageSixTokenType.RAW_STRING_LITERAL
                # Boolean literal: true / false
                case StageFourTokenType.TRUE | StageFourTokenType.FALSE:
                    return StageSixTokenType.BOOLEAN_LITERAL
                # Numeric literal: identifier whose value is all digits (e.g. "42")
                case StageFourTokenType.IDENTIFIER if tokens[0].value.isdigit():
                    return StageSixTokenType.NUMERIC_LITERAL

        # Keyword-led expressions — the first token determines the type.
        match tokens[0].token_type:
            # for x in items
            case StageFourTokenType.FOR:
                return StageSixTokenType.FOR_LOOP
            # while condition
            case StageFourTokenType.WHILE:
                return StageSixTokenType.WHILE_LOOP
            # if condition
            case StageFourTokenType.IF:
                return StageSixTokenType.IF_EXPR
            # elif condition
            case StageFourTokenType.ELIF:
                return StageSixTokenType.ELIF_EXPR
            # else
            case StageFourTokenType.ELSE:
                return StageSixTokenType.ELSE_EXPR
            # match expr
            case StageFourTokenType.MATCH:
                return StageSixTokenType.MATCH_EXPR

        # Assignment: contains the walrus operator :=
        if _has_token(tokens, StageFourTokenType.WALRUS):
            return StageSixTokenType.ASSIGNMENT

        # Function definition: contains the fat arrow =>
        if _has_token(tokens, StageFourTokenType.FAT_ARROW):
            return StageSixTokenType.FUNCTION_DEF

        # Function call: identifier immediately followed by (
        if _has_adjacent(tokens, StageFourTokenType.IDENTIFIER, StageFourTokenType.PAREN_LEFT):
            return StageSixTokenType.FUNCTION_CALL

        # Binary operation: has an operator with at least 3 tokens (left op right)
        if len(tokens) >= 3 and any(t.token_type in OPERATOR_TYPES for t in tokens):
            return StageSixTokenType.BINARY_OP

        # Fallback: unrecognized expression structure.
        return StageSixTokenType.EXPRESSION
