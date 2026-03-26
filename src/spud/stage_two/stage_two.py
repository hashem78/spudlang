from typing import Generator

from structlog import BoundLogger

from spud.core.trie import Trie, TrieNode
from spud.stage_one.stage_one import StageOne
from spud.stage_one.stage_one_token import StageOneToken
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.stage_two_token import DefinedStageTwoToken, StageTwoToken, StringLiteralStageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType


class StageTwo:
    def __init__(
        self,
        stage_one: StageOne,
        trie: Trie[StageOneTokenType, StageTwoTokenType],
        logger: BoundLogger,
    ):
        self._stage_one = stage_one
        self._trie = trie
        self._logger = logger

    _BOUNDARY_TYPES = {StageOneTokenType.SPACE, StageOneTokenType.NEW_LINE}
    _STR_CTX_INDICATORS = {StageOneTokenType.SINGLE_QUOTES, StageOneTokenType.DOUBLE_QUOTES}

    def parse(self) -> Generator[StageTwoToken, None, None]:
        """Word-boundary-aware trie matching in a single pass.

        Keywords (e.g. "for", "false") should only match as whole words,
        not as substrings inside identifiers (e.g. "lforl" should NOT match "for").

        Two boundary checks are needed:

        Lookbehind -- was the previous emitted token an identifier character?
            Tracked via ``prev_was_identifier``. If True when the trie reaches a
            terminal, the match is rejected and the buffered tokens are emitted
            as individual pass-throughs.

        Lookahead -- is the next token an identifier character?
            Instead of peeking ahead, we defer emission. When the trie matches,
            we store the composite token in ``pending`` (along with ``pending_buff``
            for rollback). The *next* token resolves the pending state:

            - Boundary token (space/newline) -- emit the composite (valid match).
            - Identifier character -- reject the match, emit buffered chars instead.

            End-of-input also confirms a pending match.
        """
        buff: list[StageOneToken] = []
        current_node: TrieNode[StageOneTokenType, StageTwoTokenType] = self._trie.root
        prev_was_identifier = False
        str_ctx_buff: list[StageOneToken] = []
        pending: DefinedStageTwoToken | None = None
        pending_buff: list[StageOneToken] = []

        prev_was_backslash = False
        tokens = self._stage_one.parse()
        for token in tokens:
            if token.token_type in self._STR_CTX_INDICATORS and not prev_was_backslash:
                str_ctx_buff = [token]
                escaped = False
                while (inner_token := next(tokens, None)) is not None:
                    str_ctx_buff.append(inner_token)
                    if inner_token.token_type == StageOneTokenType.BACKWARD_SLASH:
                        escaped = not escaped
                    elif inner_token.token_type in self._STR_CTX_INDICATORS and not escaped:
                        break
                    else:
                        escaped = False

                yield StringLiteralStageTwoToken(
                    token_type=StageTwoTokenType.STRING,
                    position=str_ctx_buff[0].position,
                    value=str_ctx_buff,
                )
                str_ctx_buff.clear()
                continue

            is_boundary = token.token_type in self._BOUNDARY_TYPES

            if pending is not None:
                if is_boundary:
                    yield pending
                    prev_was_identifier = False
                else:
                    for buffered in pending_buff:
                        yield DefinedStageTwoToken(
                            token_type=StageTwoTokenType(buffered.token_type.value),
                            position=buffered.position,
                        )
                    prev_was_identifier = True
                pending = None
                pending_buff.clear()

            if token.token_type in current_node.children:
                buff.append(token)
                current_node = current_node.children[token.token_type]

                if current_node.value is not None:
                    if prev_was_identifier:
                        for buffered in buff:
                            yield DefinedStageTwoToken(
                                token_type=StageTwoTokenType(buffered.token_type.value),
                                position=buffered.position,
                            )
                        prev_was_identifier = True
                    else:
                        pending = DefinedStageTwoToken(token_type=current_node.value, position=buff[0].position)
                        pending_buff = buff.copy()
                    buff.clear()
                    current_node = self._trie.root
            else:
                for buffered in buff:
                    yield DefinedStageTwoToken(
                        token_type=StageTwoTokenType(buffered.token_type.value),
                        position=buffered.position,
                    )
                buff.clear()
                current_node = self._trie.root
                yield DefinedStageTwoToken(
                    token_type=StageTwoTokenType(token.token_type.value),
                    position=token.position,
                )
                prev_was_identifier = not is_boundary

            prev_was_backslash = token.token_type == StageOneTokenType.BACKWARD_SLASH

        if pending is not None:
            yield pending

        for buffered in buff:
            yield DefinedStageTwoToken(
                token_type=StageTwoTokenType(buffered.token_type.value),
                position=buffered.position,
            )
