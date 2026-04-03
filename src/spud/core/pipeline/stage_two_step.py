from structlog import BoundLogger

from spud.core.pipeline.pipeline_step import PipelineStep
from spud.core.pipeline.stage_one_step import StageOneStep
from spud.core.reader_protocol import IReader
from spud.core.trie import Trie
from spud.stage_one.stage_one_token_type import StageOneTokenType
from spud.stage_two.stage_two import StageTwo
from spud.stage_two.stage_two_token_type import StageTwoTokenType


class StageTwoStep(PipelineStep):
    def __init__(self, prev: StageOneStep, trie: Trie[StageOneTokenType, StageTwoTokenType], logger: BoundLogger):
        self._prev = prev
        self._trie = trie
        self._logger = logger

    def __call__(self, source: IReader) -> StageTwo:
        s1 = self._prev(source)
        return StageTwo(s1, self._trie, self._logger)
