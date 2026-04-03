from typing import Generator

from structlog import BoundLogger

from spud.core.trie import Trie, TrieNode
from spud.stage_four.stage_four_token import StageFourToken
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_three.stage_three import StageThree
from spud.stage_three.stage_three_token import StageThreeToken
from spud.stage_three.stage_three_token_type import StageThreeTokenType

_TrieNode = TrieNode[StageThreeTokenType, StageFourTokenType]
_Trie = Trie[StageThreeTokenType, StageFourTokenType]


class StageFour:
    def __init__(self, stage_three: StageThree, trie: _Trie, logger: BoundLogger):
        self._stage_three = stage_three
        self._trie = trie
        self._logger = logger

    def parse(self) -> Generator[StageFourToken, None, None]:
        yield from self._combine_floats(self._parse_operators())

    def _parse_operators(self) -> Generator[StageFourToken, None, None]:
        """Combine symbol tokens into multi-character operators via trie matching.

        No word-boundary logic is needed since stage three already splits
        symbols from identifiers. Uses longest-match: when the trie can't
        advance further, emits the last completed match and reprocesses
        any leftover tokens.
        """
        buff: list[StageThreeToken] = []
        current_node: _TrieNode = self._trie.root
        last_match: StageFourTokenType | None = None
        last_match_len: int = 0

        for token in self._stage_three.parse():
            # Token continues a trie path — keep going.
            if token.token_type in current_node.children:
                buff.append(token)
                current_node = current_node.children[token.token_type]
                # Record if this is a valid terminal.
                if current_node.value is not None:
                    last_match = current_node.value
                    last_match_len = len(buff)
                continue

            # Token breaks the trie path — emit what we have.
            yield from self._emit_match_or_flush(buff, last_match, last_match_len)
            buff.clear()
            current_node = self._trie.root
            last_match = None
            last_match_len = 0

            # Try starting a new trie path with the current token.
            if token.token_type in self._trie.root.children:
                buff.append(token)
                current_node = self._trie.root.children[token.token_type]
                if current_node.value is not None:
                    last_match = current_node.value
                    last_match_len = len(buff)
            else:
                # Non-symbol token — pass through directly.
                yield self._pass_through(token)

        # End of input — emit any remaining match or buffer.
        yield from self._emit_match_or_flush(buff, last_match, last_match_len)

    def _emit_match_or_flush(
        self,
        buff: list[StageThreeToken],
        last_match: StageFourTokenType | None,
        last_match_len: int,
    ) -> Generator[StageFourToken, None, None]:
        if last_match is not None:
            # Emit the longest match.
            yield StageFourToken(
                token_type=last_match,
                position=buff[0].position,
                value="".join(t.value for t in buff[:last_match_len]),
            )
            # Pass through any tokens beyond the match.
            for leftover in buff[last_match_len:]:
                yield self._pass_through(leftover)
        else:
            # No match — pass through everything.
            for token in buff:
                yield self._pass_through(token)

    @staticmethod
    def _pass_through(token: StageThreeToken) -> StageFourToken:
        try:
            token_type = StageFourTokenType[token.token_type.name]
        except KeyError:
            token_type = StageFourTokenType.UNKNOWN
        return StageFourToken(
            token_type=token_type,
            position=token.position,
            value=token.value,
        )

    @staticmethod
    def _combine_floats(
        stream: Generator[StageFourToken, None, None],
    ) -> Generator[StageFourToken, None, None]:
        T = StageFourTokenType
        pending: list[StageFourToken] = []

        def _make_float(tokens: list[StageFourToken]) -> StageFourToken:
            return StageFourToken(
                token_type=T.FLOAT,
                position=tokens[0].position,
                value="".join(t.value for t in tokens),
            )

        def _start(tok: StageFourToken) -> bool:
            if tok.token_type in (T.INT, T.DOT):
                pending.append(tok)
                return True
            return False

        for token in stream:
            if not pending:
                if not _start(token):
                    yield token
                continue

            match len(pending):
                case 1 if pending[0].token_type == T.INT:
                    if token.token_type == T.DOT:
                        pending.append(token)
                    else:
                        yield pending[0]
                        pending.clear()
                        if not _start(token):
                            yield token

                case 1 if pending[0].token_type == T.DOT:
                    if token.token_type == T.INT:
                        yield _make_float([pending[0], token])
                        pending.clear()
                    else:
                        yield pending[0]
                        pending.clear()
                        if not _start(token):
                            yield token

                case 2:
                    if token.token_type == T.INT:
                        yield _make_float([pending[0], pending[1], token])
                        pending.clear()
                    else:
                        yield _make_float(pending)
                        pending.clear()
                        if not _start(token):
                            yield token

        if pending:
            if len(pending) == 2:
                yield _make_float(pending)
            else:
                yield pending[0]
