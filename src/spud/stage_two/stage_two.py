from typing import Generator

from structlog import BoundLogger

from spud.core.pipeline.pipeline_stage import PipelineStage
from spud.core.trie import Trie
from spud.stage_one.stage_one import StageOne
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.keyword_pass import KeywordPass
from spud.stage_two.stage_two_token import StageTwoToken
from spud.stage_two.stage_two_token_type import StageTwoTokenType
from spud.stage_two.string_pass import StringPass


class StageTwo(PipelineStage):
    def __init__(
        self,
        stage_one: StageOne,
        trie: Trie[StageOneTokenType, StageTwoTokenType],
        logger: BoundLogger,
    ):
        self._stage_one = stage_one
        self._trie = trie
        self._logger = logger

    def parse(self) -> Generator[StageTwoToken, None, None]:
        string_pass = StringPass(self._stage_one)
        keyword_pass = KeywordPass(string_pass, self._trie)
        yield from keyword_pass.parse()
