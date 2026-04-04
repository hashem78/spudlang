from pydantic import BaseModel

from spud.stage_six.identifier import Identifier
from spud.stage_six.type_expression import TypeExpression


class TypedParam(BaseModel, frozen=True):
    name: Identifier
    type_annotation: TypeExpression
