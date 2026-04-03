from structlog import BoundLogger

from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.stage_three_step import StageThreeStep
from spud.core.reader_protocol import IReader
from spud.core.trie import Trie
from spud.stage_four.stage_four import StageFour
from spud.stage_four.stage_four_token_type import StageFourTokenType
from spud.stage_three.stage_three_token_type import StageThreeTokenType


class StageFourStep(PipelineStep):
    def __init__(
        self,
        prev: StageThreeStep,
        trie: Trie[StageThreeTokenType, StageFourTokenType],
        logger: BoundLogger,
    ):
        self._prev = prev
        self._trie = trie
        self._logger = logger

    def __call__(self, source: IReader) -> StageFour:
        s3 = self._prev(source)
        return StageFour(s3, self._trie, self._logger)
