from typing import Generator

from structlog import BoundLogger

from spud.core.position import Position
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType
from spud.stage_four.stage_four import StageFour
from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_four.stage_four_token_type import StageFourTokenType

_Line = tuple[int, list[StageFourToken]]
_LineIter = Generator[_Line, None, None]

_TYPE_MAP = {
    member.value: StageFiveTokenType(member.value)
    for member in StageFourTokenType
    if member != StageFourTokenType.NEW_LINE
}


class StageFive:
    """Transform a stream of stage four tokens into a flat stream with
    INDENT/DEDENT markers that encode nesting structure.

    Stage four emits tokens with NEW_LINE separators. This stage groups
    those tokens into lines, tracks indentation changes via a stack of
    column positions, and injects synthetic INDENT, DEDENT, and NEW_LINE
    tokens into the output stream.

    The output is fully streaming — one token at a time, no tree built.
    Memory usage is O(line length + nesting depth).

    Example — given this input::

        parent
          child1
          child2
        sibling

    The output stream is::

        parent NEW_LINE INDENT child1 NEW_LINE child2 NEW_LINE DEDENT sibling NEW_LINE

    The indent stack tracks which column positions have open blocks.
    It starts at ``[0]``. When a deeper column is seen, it is pushed
    and an INDENT is emitted. When a shallower column is seen, levels
    are popped (with a DEDENT each) until the stack top matches.
    At end-of-input, all remaining levels above the base are closed.
    """

    def __init__(self, stage_four: StageFour, logger: BoundLogger):
        self._stage_four = stage_four
        self._logger = logger

    def parse(self) -> Generator[StageFiveToken, None, None]:
        """Emit a flat token stream with INDENT/DEDENT nesting markers.

        Algorithm:

        1. ``_line_iter`` groups stage four tokens into lines, yielding
           ``(indent_column, tokens)`` one line at a time. Blank lines
           are filtered out.

        2. For each line, compare its indent column to the top of the
           indent stack:

           - **Deeper** (indent > stack top): a new block is opening.
             Push the column onto the stack and emit INDENT before
             the line's tokens.

           - **Shallower** (indent < stack top): one or more blocks are
             closing. Pop and emit DEDENT for each level until the stack
             top matches the current indent. This handles multi-level
             dedents (e.g. column 8 → column 0 emits multiple DEDENTs).

           - **Same** (indent == stack top): continuation of the current
             block. No INDENT or DEDENT — just emit the tokens.

        3. After the line's tokens, emit NEW_LINE as an expression
           boundary.

        4. When the input is exhausted, emit DEDENT for every level
           still open above the base (stack has more than one entry).
        """
        # The indent stack tracks open block levels by column position.
        # It always starts with [0] — the base level. Each entry means
        # "there is an open block at this column." We push on INDENT
        # and pop on DEDENT, so the stack depth == nesting depth + 1.
        indent_stack: list[int] = [0]
        last_pos = Position(line=0, column=0)

        for indent, tokens in self._line_iter():
            # ── Indent increased: new block opens ────────────────
            # The line is deeper than the current block. Record its
            # column as a new indent level and emit INDENT so the
            # parser knows a nested body is starting.
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                yield self._make(StageFiveTokenType.INDENT, tokens[0].position)

            # ── Indent decreased: one or more blocks close ───────
            # The line is shallower than the current block. Pop
            # levels off the stack until the top matches, emitting
            # DEDENT for each closed block. This is a while loop
            # because a single line can close multiple levels
            # (e.g. jumping from column 8 back to column 0).
            while indent < indent_stack[-1]:
                indent_stack.pop()
                yield self._make(StageFiveTokenType.DEDENT, tokens[0].position)

            # ── Emit the line's tokens ───────────────────────────
            # If indent == stack top, we fall through here directly
            # — the line is a sibling in the current block, so no
            # INDENT or DEDENT is needed.
            for token in tokens:
                yield self._convert(token)

            # ── Expression boundary ──────────────────────────────
            # NEW_LINE marks the end of this expression. The parser
            # uses this to know where one statement ends.
            last_pos = tokens[-1].position
            yield self._make(StageFiveTokenType.NEW_LINE, last_pos)

        # ── End of input: close all remaining blocks ─────────────
        # If the file ends while blocks are still open (stack has
        # more than the base entry), emit DEDENT for each. Without
        # this, the parser would see unclosed blocks.
        while len(indent_stack) > 1:
            indent_stack.pop()
            yield self._make(StageFiveTokenType.DEDENT, last_pos)

    def _line_iter(self) -> _LineIter:
        """Group stage four tokens into lines, yielding one at a time.

        Consumes the stage four stream and buffers tokens until a
        NEW_LINE is encountered. Then yields ``(indent, tokens)``
        where indent is the column position of the first token on
        that line. The line's tokens are buffered because we need
        the first token's column to determine the indent level
        before we can decide whether to emit INDENT or DEDENT.

        Blank lines (NEW_LINE immediately after NEW_LINE) produce
        an empty buffer and are silently skipped.

        The trailing line (tokens after the last NEW_LINE, or the
        entire input if there are no newlines) is yielded when the
        stage four stream is exhausted.
        """
        current_line: list[StageFourToken] = []

        for token in self._stage_four.parse():
            # NEW_LINE ends the current line. If the buffer is
            # non-empty, yield it and reset. If empty, this was
            # a blank line — skip it.
            if token.token_type == StageFourTokenType.NEW_LINE:
                if current_line:
                    indent = current_line[0].position.column
                    yield indent, current_line
                    current_line = []
            # Any other token is part of the current line.
            else:
                current_line.append(token)

        # Yield the final line if the input didn't end with a newline.
        if current_line:
            indent = current_line[0].position.column
            yield indent, current_line

    def _convert(self, token: StageFourToken) -> StageFiveToken:
        """Convert a stage four token to a stage five token."""
        return StageFiveToken(
            token_type=_TYPE_MAP[token.token_type.value],
            position=token.position,
            value=token.value,
        )

    def _make(self, token_type: StageFiveTokenType, position: Position) -> StageFiveToken:
        """Create a synthetic stage five token (INDENT, DEDENT, NEW_LINE)."""
        return StageFiveToken(
            token_type=token_type,
            position=position,
            value="",
        )
