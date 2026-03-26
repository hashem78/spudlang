from typing import Generator

from structlog import BoundLogger

from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_four.stage_four import StageFour
from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_four.stage_four_token_type import StageFourTokenType

_Line = tuple[int, list[StageFourToken]]
_LineIter = Generator[_Line, None, None]


class StageFive:
    def __init__(self, stage_four: StageFour, logger: BoundLogger):
        self._stage_four = stage_four
        self._logger = logger

    def parse(self) -> Generator[StageFiveToken, None, None]:
        """Group stage four tokens into indentation-aware nested expressions.

        Each non-empty line becomes an expression. Lines indented deeper
        than their predecessor become children of that expression.
        Indentation is derived from the first token's column position.

        Uses a streaming approach with one-line lookahead. Memory usage
        is O(nesting depth) rather than O(file size).
        """
        line_iter = self._line_iter()
        expressions, _ = self._build_expressions(line_iter, -1, None)
        yield from expressions

    def _line_iter(self) -> _LineIter:
        """Yield (indent, tokens) tuples one line at a time from stage four."""
        current_line: list[StageFourToken] = []

        for token in self._stage_four.parse():
            if token.token_type == StageFourTokenType.NEW_LINE:
                if current_line:
                    indent = current_line[0].position.column
                    yield indent, current_line
                    current_line = []
            else:
                current_line.append(token)

        if current_line:
            indent = current_line[0].position.column
            yield indent, current_line

    def _build_expressions(
        self, line_iter: _LineIter, parent_indent: int, leftover: _Line | None
    ) -> tuple[list[StageFiveToken], _Line | None]:
        """Recursively build nested expressions from a streaming line iterator.

        Pulls lines one at a time from the shared ``line_iter``. When a
        line is indented deeper than the current expression, it recurses
        to collect children. When a line is too shallow, it returns that
        line as leftover for the caller to process.

        Args:
            line_iter: Shared generator of (indent, tokens) lines.
            parent_indent: Indent level of the caller. Lines at or below
                this level belong to a parent scope.
            leftover: A line returned by a child call that was too shallow
                for it. Consumed before pulling from line_iter.

        Returns:
            (expressions, leftover) where leftover is a line that was
            too shallow for this scope, or None if the iterator is exhausted.
        """
        expressions: list[StageFiveToken] = []

        # Get first line — from leftover or iterator.
        line = leftover if leftover is not None else next(line_iter, None)

        while line is not None:
            indent, tokens = line

            # This line belongs to a parent scope — return it as leftover.
            if indent <= parent_indent:
                return expressions, line

            # Create expression from this line.
            expr = StageFiveToken(
                token_type=StageFiveTokenType.EXPRESSION,
                position=tokens[0].position,
                tokens=tokens,
            )

            # Peek at next line to check for children.
            next_line = next(line_iter, None)

            if next_line is not None and next_line[0] > indent:
                # Next line is deeper — recurse to collect children.
                expr.children, line = self._build_expressions(line_iter, indent, next_line)
            else:
                # Same level, shallower, or end of input — no children.
                line = next_line

            expressions.append(expr)

        return expressions, None
