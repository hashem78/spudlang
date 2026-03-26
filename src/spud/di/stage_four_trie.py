from spud.core.trie import Trie
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_three.stage_three_token_type import StageThreeTokenType


def create_stage_four_trie() -> Trie[StageThreeTokenType, StageFourTokenType]:
    trie: Trie[StageThreeTokenType, StageFourTokenType] = Trie()

    trie.insert(
        [StageThreeTokenType.COLON, StageThreeTokenType.EQUALS],
        StageFourTokenType.WALRUS,
    )
    trie.insert(
        [StageThreeTokenType.EQUALS],
        StageFourTokenType.ASSIGN,
    )
    trie.insert(
        [StageThreeTokenType.EQUALS, StageThreeTokenType.EQUALS],
        StageFourTokenType.EQUALS,
    )
    trie.insert(
        [StageThreeTokenType.EXCLAMATION, StageThreeTokenType.EQUALS],
        StageFourTokenType.NOT_EQUALS,
    )
    trie.insert(
        [StageThreeTokenType.ANGLED_LEFT],
        StageFourTokenType.LESS_THAN,
    )
    trie.insert(
        [StageThreeTokenType.ANGLED_RIGHT],
        StageFourTokenType.GREATER_THAN,
    )
    trie.insert(
        [StageThreeTokenType.ANGLED_LEFT, StageThreeTokenType.EQUALS],
        StageFourTokenType.LESS_THAN_OR_EQUAL,
    )
    trie.insert(
        [StageThreeTokenType.ANGLED_RIGHT, StageThreeTokenType.EQUALS],
        StageFourTokenType.GREATER_THAN_OR_EQUAL,
    )
    trie.insert(
        [StageThreeTokenType.PLUS],
        StageFourTokenType.PLUS,
    )
    trie.insert(
        [StageThreeTokenType.HYPHEN],
        StageFourTokenType.MINUS,
    )
    trie.insert(
        [StageThreeTokenType.ASTERISK],
        StageFourTokenType.MULTIPLY,
    )
    trie.insert(
        [StageThreeTokenType.FORWARD_SLASH],
        StageFourTokenType.DIVIDE,
    )
    trie.insert(
        [StageThreeTokenType.PERCENT],
        StageFourTokenType.MODULO,
    )
    trie.insert(
        [StageThreeTokenType.AMPERSAND, StageThreeTokenType.AMPERSAND],
        StageFourTokenType.LOGICAL_AND,
    )
    trie.insert(
        [StageThreeTokenType.PIPE, StageThreeTokenType.PIPE],
        StageFourTokenType.LOGICAL_OR,
    )
    trie.insert(
        [StageThreeTokenType.HYPHEN, StageThreeTokenType.ANGLED_RIGHT],
        StageFourTokenType.ARROW,
    )
    trie.insert(
        [StageThreeTokenType.EQUALS, StageThreeTokenType.ANGLED_RIGHT],
        StageFourTokenType.FAT_ARROW,
    )
    trie.insert(
        [StageThreeTokenType.COLON, StageThreeTokenType.COLON],
        StageFourTokenType.PATH_SEPARATOR,
    )

    return trie
