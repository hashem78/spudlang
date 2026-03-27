from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_six.stage_six_token import StageSixToken
from spud.stage_six.token_helpers import OPERATOR_TYPES, _find_token, _has_adjacent, _has_token, _make_node


class DecomposePass:
    """Structurally split expressions into sub-expression children.

    This is a recursive descent over the expression tree. For each
    expression it:

    1. Recursively decomposes all stage-five indented children first
       (bottom-up), producing ``body_children``.
    2. Examines its own tokens to decide how to split them into
       structural sub-expressions.
    3. Creates new child nodes from the split, attaching body_children
       to the structurally correct parent.

    All nodes are created with EXPRESSION as a placeholder type —
    the classify pass assigns real types afterward.

    Decision tree for ``_decompose``::

        tokens empty?           → leaf node with body children
        has :=?                 → assignment (split at :=)
        starts with FOR?        → for loop (split at IN)
        starts with WHILE?      → while (condition after keyword)
        starts with IF/ELIF?    → conditional (condition after keyword)
        starts with ELSE/MATCH? → no split, just attach body
        has ident(?             → function call (callee + args)
        has operator (3+ tok)?  → binary op (split at first operator)
        none of the above?      → no split, just attach body
    """

    def process(self, expr: StageFiveToken) -> StageSixToken:
        """Entry point: decompose a stage-five expression and all its descendants."""
        body_children = [self.process(c) for c in expr.children]
        return self._decompose(expr.tokens, body_children, expr)

    def _decompose(
        self,
        tokens: list[StageFourToken],
        body_children: list[StageSixToken],
        expr: StageFiveToken,
    ) -> StageSixToken:
        """Route tokens to the appropriate decomposer based on their content."""
        # No tokens — just a container for body children.
        if not tokens:
            return _make_node(tokens, body_children)

        # Assignment takes priority — split at the := operator.
        walrus_idx = _find_token(tokens, StageFourTokenType.WALRUS)
        if walrus_idx is not None:
            return self._decompose_assignment(tokens, walrus_idx, body_children, expr)

        # Keyword-led expressions — the first token determines the structure.
        match tokens[0].token_type:
            # FOR: split into variable, iterable, and body.
            case StageFourTokenType.FOR:
                return self._decompose_for(tokens, body_children, expr)
            # WHILE: extract condition, attach body.
            case StageFourTokenType.WHILE:
                return self._decompose_keyword_condition(tokens, body_children, expr)
            # IF/ELIF: extract condition, attach body.
            case StageFourTokenType.IF | StageFourTokenType.ELIF:
                return self._decompose_keyword_condition(tokens, body_children, expr)
            # ELSE/MATCH: no condition to extract, just attach body.
            case StageFourTokenType.ELSE | StageFourTokenType.MATCH:
                return _make_node(tokens, body_children)

        # Function call: identifier immediately followed by opening paren.
        if _has_adjacent(tokens, StageFourTokenType.IDENTIFIER, StageFourTokenType.PAREN_LEFT):
            return self._decompose_function_call(tokens, body_children, expr)

        # Binary operation: at least 3 tokens with an operator between operands.
        if len(tokens) >= 3 and any(t.token_type in OPERATOR_TYPES for t in tokens):
            return self._decompose_binary_op(tokens, body_children, expr)

        # Fallback: no structural split. Literals, single identifiers, etc.
        return _make_node(tokens, body_children)

    def _decompose_assignment(
        self, tokens: list[StageFourToken], walrus_idx: int, body_children: list[StageSixToken], expr: StageFiveToken
    ) -> StageSixToken:
        """Split ``target := value`` into target and value children.

        The target (left of :=) is recursively decomposed.
        The value (right of :=) is recursively decomposed.

        If the value contains a fat arrow (=>), the indented body children
        belong to the function definition, not the assignment. Otherwise
        they attach to the assignment itself.
        """
        left_tokens = tokens[:walrus_idx]
        right_tokens = tokens[walrus_idx + 1:]

        # Target is always a standalone sub-expression (no body children).
        target = self._decompose(left_tokens, [], expr)

        # If value is a function def, body children are the function's body.
        if _has_token(right_tokens, StageFourTokenType.FAT_ARROW):
            value = self._decompose(right_tokens, body_children, expr)
            return _make_node(tokens, [target, value])

        # Otherwise body children belong to the assignment.
        value = self._decompose(right_tokens, [], expr)
        return _make_node(tokens, [target, value] + body_children)

    def _decompose_for(
        self, tokens: list[StageFourToken], body_children: list[StageSixToken], expr: StageFiveToken
    ) -> StageSixToken:
        """Split ``for variable in iterable`` into variable, iterable, and body.

        Tokens between FOR and IN become the variable sub-expression.
        Tokens after IN become the iterable sub-expression (which may
        itself be a function call like ``range(n)``).
        Body children from indentation become the loop body.
        """
        in_idx = _find_token(tokens, StageFourTokenType.IN)
        # Malformed for loop without IN — treat as opaque.
        if in_idx is None:
            return _make_node(tokens, body_children)

        variable_tokens = tokens[1:in_idx]
        iterable_tokens = tokens[in_idx + 1:]

        children: list[StageSixToken] = []
        if variable_tokens:
            children.append(self._decompose(variable_tokens, [], expr))
        if iterable_tokens:
            children.append(self._decompose(iterable_tokens, [], expr))
        # Body children (the indented block) come after variable and iterable.
        children.extend(body_children)

        return _make_node(tokens, children)

    def _decompose_keyword_condition(
        self,
        tokens: list[StageFourToken],
        body_children: list[StageSixToken],
        expr: StageFiveToken,
    ) -> StageSixToken:
        """Split ``if/elif/while condition`` into condition and body.

        Tokens after the keyword become the condition sub-expression
        (which may itself be a binary op like ``i > 5``).
        Body children from indentation follow the condition.
        """
        condition_tokens = tokens[1:]
        children: list[StageSixToken] = []
        if condition_tokens:
            children.append(self._decompose(condition_tokens, [], expr))
        children.extend(body_children)
        return _make_node(tokens, children)

    def _decompose_function_call(
        self,
        tokens: list[StageFourToken],
        body_children: list[StageSixToken],
        expr: StageFiveToken,
    ) -> StageSixToken:
        """Split ``callee(arg1, arg2)`` into callee and argument children.

        Tokens before the first ``(`` become the callee sub-expression.
        Tokens inside the parens are split on commas — each segment
        becomes an argument sub-expression, recursively decomposed.
        """
        paren_idx = _find_token(tokens, StageFourTokenType.PAREN_LEFT)
        # Safety: shouldn't happen since _has_adjacent already checked.
        if paren_idx is None:
            return _make_node(tokens, body_children)

        # Everything before ( is the callee (e.g. function name).
        callee_tokens = tokens[:paren_idx]
        # Everything between ( and ) is the argument list.
        inner_tokens = tokens[paren_idx + 1:]
        if inner_tokens and inner_tokens[-1].token_type == StageFourTokenType.PAREN_RIGHT:
            inner_tokens = inner_tokens[:-1]

        children: list[StageSixToken] = []
        if callee_tokens:
            children.append(self._decompose(callee_tokens, [], expr))

        # Split arguments on commas. Each comma-separated segment is
        # one argument, recursively decomposed (so ``f(a + b, c)``
        # produces a BINARY_OP arg and an EXPRESSION arg).
        current_arg: list[StageFourToken] = []
        for token in inner_tokens:
            if token.token_type == StageFourTokenType.COMMA:
                if current_arg:
                    children.append(self._decompose(current_arg, [], expr))
                    current_arg = []
            else:
                current_arg.append(token)
        if current_arg:
            children.append(self._decompose(current_arg, [], expr))

        children.extend(body_children)
        return _make_node(tokens, children)

    def _decompose_binary_op(
        self,
        tokens: list[StageFourToken],
        body_children: list[StageSixToken],
        expr: StageFiveToken,
    ) -> StageSixToken:
        """Split at the first operator into left and right operand children.

        The left operand (tokens before the operator) and right operand
        (tokens after) are both recursively decomposed. This means
        chained operations like ``a + b * c`` split at ``+`` first,
        then ``b * c`` splits at ``*`` in the recursive call.
        """
        op_idx = next(i for i, t in enumerate(tokens) if t.token_type in OPERATOR_TYPES)
        left_tokens = tokens[:op_idx]
        right_tokens = tokens[op_idx + 1:]

        children: list[StageSixToken] = []
        if left_tokens:
            children.append(self._decompose(left_tokens, [], expr))
        if right_tokens:
            children.append(self._decompose(right_tokens, [], expr))
        children.extend(body_children)
        return _make_node(tokens, children)
