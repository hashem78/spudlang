from enum import Enum, auto
from typing import Generator

from pydantic import BaseModel, ConfigDict

from spud.core.trie import Trie, TrieNode
from spud.stage_one.stage_one_token import StageOneToken
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.stage_two_token import DefinedStageTwoToken, StageTwoToken, StringLiteralStageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType
from spud.stage_two.string_pass import StringPass

_TrieNode = TrieNode[StageOneTokenType, StageTwoTokenType]
_Trie = Trie[StageOneTokenType, StageTwoTokenType]
_Emitted = tuple[StageTwoToken, ...]
_Transition = tuple["_State", _Emitted]


class _Phase(Enum):
    """Boundary context for keyword matching.

    AFTER_BOUNDARY -- previous token was a word boundary (space, newline,
        string literal, or start-of-input). Trie matches are accepted.

    AFTER_IDENTIFIER -- previous token was an identifier character.
        Trie matches are rejected because the keyword would be a substring.

    PENDING_MATCH -- the trie completed a match but we haven't seen the
        next token yet. The match is deferred until the next token confirms
        whether a word boundary follows.
    """

    AFTER_BOUNDARY = auto()
    AFTER_IDENTIFIER = auto()
    PENDING_MATCH = auto()


class _State(BaseModel):
    """Immutable snapshot of the keyword pass state.

    All transitions return a new ``_State`` via ``model_copy``.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    phase: _Phase = _Phase.AFTER_BOUNDARY
    buff: tuple[StageOneToken, ...] = ()
    current_node: _TrieNode
    pending_token: DefinedStageTwoToken | None = None
    pending_buff: tuple[StageOneToken, ...] = ()

    def with_phase(self, phase: _Phase) -> "_State":
        return self.model_copy(update={"phase": phase})

    def reset_trie(self, root: _TrieNode) -> "_State":
        return self.model_copy(update={"buff": (), "current_node": root})

    def clear_pending(self) -> "_State":
        return self.model_copy(update={"pending_token": None, "pending_buff": ()})

    def advance(self, token: StageOneToken, child: _TrieNode) -> "_State":
        return self.model_copy(update={"buff": (*self.buff, token), "current_node": child})

    def set_pending(self, token: DefinedStageTwoToken, buff: tuple[StageOneToken, ...]) -> "_State":
        return self.model_copy(
            update={
                "pending_token": token,
                "pending_buff": buff,
                "phase": _Phase.PENDING_MATCH,
            }
        )


def _to_defined(token: StageOneToken) -> DefinedStageTwoToken:
    """Convert a stage-one token into a pass-through stage-two token."""
    return DefinedStageTwoToken(
        token_type=StageTwoTokenType(token.token_type.value),
        position=token.position,
    )


def _flush(tokens: tuple[StageOneToken, ...]) -> _Emitted:
    """Convert a buffer of stage-one tokens into pass-through stage-two tokens."""
    return tuple(_to_defined(t) for t in tokens)


class KeywordPass:
    """Matches keyword sequences from a trie while respecting word boundaries.

    Consumes tokens from a ``StringPass``. String literals are yielded
    as-is; all other tokens go through the trie.

    The matching algorithm has two boundary checks:

    Lookbehind
        Encoded in the phase. If the phase is ``AFTER_IDENTIFIER`` when
        the trie reaches a terminal node, the match is rejected and the
        buffered tokens are emitted as individual pass-throughs.

    Lookahead
        When the trie reaches a terminal node in ``AFTER_BOUNDARY``, the
        match is not emitted immediately. Instead it is stored as a pending
        match (``PENDING_MATCH``). The *next* token resolves it:

        - Boundary token (space/newline) confirms the match.
        - Identifier character rejects it; the buffered tokens are rolled
          back as pass-throughs.

        End-of-input also confirms a pending match.
    """

    _BOUNDARY_TYPES = {StageOneTokenType.SPACE, StageOneTokenType.NEW_LINE}

    def __init__(self, string_pass: StringPass, trie: _Trie):
        self._string_pass = string_pass
        self._trie = trie

    def parse(self) -> Generator[StageTwoToken, None, None]:
        """Run the keyword pass over the string pass output."""
        s = _State(current_node=self._trie.root)

        for token in self._string_pass.parse():
            # String literals bypass trie matching entirely. Any in-progress
            # trie state is flushed and the string is yielded as-is.
            if isinstance(token, StringLiteralStageTwoToken):
                # A pending keyword before a string is valid — the string
                # acts as a word boundary.
                if s.phase == _Phase.PENDING_MATCH:
                    assert s.pending_token is not None
                    yield s.pending_token
                # Flush any partially-matched trie buffer as pass-throughs.
                yield from _flush(s.buff)
                s = s.clear_pending().reset_trie(self._trie.root).with_phase(_Phase.AFTER_BOUNDARY)
                yield token
                continue

            is_boundary = token.token_type in self._BOUNDARY_TYPES

            # Step 1: If we have a pending keyword match, the current token
            # determines whether it's confirmed (boundary) or rejected (identifier).
            s, emitted = self._resolve_pending(s, is_boundary)
            yield from emitted

            # Step 2: Feed the current token into the trie.
            s, emitted = self._advance_trie(s, token, is_boundary)
            yield from emitted

        # End of input: a pending match is confirmed since nothing follows.
        if s.phase == _Phase.PENDING_MATCH:
            assert s.pending_token is not None
            yield s.pending_token

        # Flush any remaining partially-matched buffer as pass-throughs.
        yield from _flush(s.buff)

    def _resolve_pending(self, s: _State, is_boundary: bool) -> _Transition:
        """Resolve a pending keyword match using the current token as lookahead.

        If the current token is a boundary, the pending keyword is confirmed.
        Otherwise the match is rejected and the buffered tokens are rolled back.
        """
        # Not in PENDING_MATCH — nothing to resolve.
        if s.phase != _Phase.PENDING_MATCH:
            return s, ()

        assert s.pending_token is not None

        # Boundary confirms the keyword — emit it.
        if is_boundary:
            return s.clear_pending().with_phase(_Phase.AFTER_BOUNDARY), (s.pending_token,)

        # Identifier character rejects the keyword — roll back the buffered
        # tokens as individual pass-throughs.
        return s.clear_pending().with_phase(_Phase.AFTER_IDENTIFIER), _flush(s.pending_buff)

    def _advance_trie(self, s: _State, token: StageOneToken, is_boundary: bool) -> _Transition:
        """Advance the trie with the current token.

        Three outcomes:
        - Token has no matching child: flush buffer, emit token as pass-through.
        - Token matches a child but not a terminal: buffer token, continue.
        - Token matches a terminal: delegate to ``_complete_match``.
        """
        # No matching child in the trie — this token breaks the current path.
        if token.token_type not in s.current_node.children:
            return self._no_match(s, token, is_boundary)

        child = s.current_node.children[token.token_type]
        new_buff = (*s.buff, token)

        # Matched a child but not at a terminal — keep walking the trie.
        if child.value is None:
            return s.advance(token, child), ()

        # Reached a terminal node — a keyword sequence is fully matched.
        return self._complete_match(s, child.value, new_buff)

    def _no_match(self, s: _State, token: StageOneToken, is_boundary: bool) -> _Transition:
        """Handle a token that doesn't continue any trie path.

        Flushes any buffered tokens and the current token as pass-throughs.
        """
        phase = _Phase.AFTER_BOUNDARY if is_boundary else _Phase.AFTER_IDENTIFIER
        emitted = _flush(s.buff) + (_to_defined(token),)
        return s.reset_trie(self._trie.root).with_phase(phase), emitted

    def _complete_match(self, s: _State, value: StageTwoTokenType, new_buff: tuple[StageOneToken, ...]) -> _Transition:
        """Handle a completed trie match.

        In ``AFTER_BOUNDARY``: the match is valid but deferred as pending
        until the next token confirms the trailing word boundary.

        In ``AFTER_IDENTIFIER``: the match is rejected (lookbehind fails)
        and the buffered tokens are emitted as individual pass-throughs.
        """
        match s.phase:
            # Valid leading boundary — defer the match until the next token
            # confirms the trailing boundary.
            case _Phase.AFTER_BOUNDARY:
                pending = DefinedStageTwoToken(token_type=value, position=new_buff[0].position)
                return s.reset_trie(self._trie.root).set_pending(pending, new_buff), ()
            # Previous token was an identifier char — this keyword is a
            # substring, not a standalone word. Reject and emit as chars.
            case _Phase.AFTER_IDENTIFIER:
                return s.reset_trie(self._trie.root).with_phase(_Phase.AFTER_IDENTIFIER), _flush(new_buff)
            case _:
                return s.reset_trie(self._trie.root), ()
