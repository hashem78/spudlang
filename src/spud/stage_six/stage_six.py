from typing import Generator

from structlog import BoundLogger

from spud.stage_five.stage_five import StageFive
from spud.stage_six.classify_pass import ClassifyPass
from spud.stage_six.decompose_pass import DecomposePass
from spud.stage_six.stage_six_token import StageSixToken


class StageSix:
    def __init__(self, stage_five: StageFive, logger: BoundLogger):
        self._stage_five = stage_five
        self._logger = logger

    def parse(self) -> Generator[StageSixToken, None, None]:
        """Decompose and classify stage five expressions."""
        decompose = DecomposePass()
        classify = ClassifyPass()
        for expr in self._stage_five.parse():
            decomposed = decompose.process(expr)
            classified = classify.process(decomposed)
            yield classified
