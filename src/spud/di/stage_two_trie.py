from spud.core.trie import Trie
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.stage_two import StageTwoTokenType


def create_stage_two_trie() -> Trie[StageOneTokenType, StageTwoTokenType]:
    trie: Trie[StageOneTokenType, StageTwoTokenType] = Trie()

    trie.insert(
        [
            StageOneTokenType.F_LOWERCASE,
            StageOneTokenType.A_LOWERCASE,
            StageOneTokenType.L_LOWERCASE,
            StageOneTokenType.S_LOWERCASE,
            StageOneTokenType.E_LOWERCASE,
        ],
        StageTwoTokenType.FALSE,
    )
    trie.insert(
        [
            StageOneTokenType.T_LOWERCASE,
            StageOneTokenType.R_LOWERCASE,
            StageOneTokenType.U_LOWERCASE,
            StageOneTokenType.E_LOWERCASE,
        ],
        StageTwoTokenType.TRUE,
    )
    trie.insert(
        [
            StageOneTokenType.I_LOWERCASE,
            StageOneTokenType.F_LOWERCASE,
        ],
        StageTwoTokenType.IF,
    )
    trie.insert(
        [
            StageOneTokenType.F_LOWERCASE,
            StageOneTokenType.O_LOWERCASE,
            StageOneTokenType.R_LOWERCASE,
        ],
        StageTwoTokenType.FOR,
    )
    trie.insert(
        [
            StageOneTokenType.W_LOWERCASE,
            StageOneTokenType.H_LOWERCASE,
            StageOneTokenType.I_LOWERCASE,
            StageOneTokenType.L_LOWERCASE,
            StageOneTokenType.E_LOWERCASE,
        ],
        StageTwoTokenType.WHILE,
    )
    trie.insert(
        [
            StageOneTokenType.O_LOWERCASE,
            StageOneTokenType.R_LOWERCASE,
        ],
        StageTwoTokenType.OR,
    )
    trie.insert(
        [
            StageOneTokenType.A_LOWERCASE,
            StageOneTokenType.N_LOWERCASE,
            StageOneTokenType.D_LOWERCASE,
        ],
        StageTwoTokenType.AND,
    )
    trie.insert(
        [
            StageOneTokenType.I_LOWERCASE,
            StageOneTokenType.N_LOWERCASE,
        ],
        StageTwoTokenType.IN,
    )

    trie.insert(
        [
            StageOneTokenType.E_LOWERCASE,
            StageOneTokenType.L_LOWERCASE,
            StageOneTokenType.S_LOWERCASE,
            StageOneTokenType.E_LOWERCASE,
        ],
        StageTwoTokenType.ELSE,
    )

    return trie
