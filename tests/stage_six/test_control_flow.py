from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.program import Program
from spud.stage_six.string_literal import StringLiteral
from tests.stage_six.helpers import parse


class TestIfElse:
    def test_if_only(self):
        result = parse('if x > 0\n  "positive"')
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 1
        assert node.else_body is None
        branch = node.branches[0]
        assert isinstance(branch, ConditionBranch)
        assert isinstance(branch.condition, BinaryOp)
        assert branch.condition.operator == ">"
        assert len(branch.body) == 1
        assert isinstance(branch.body[0], StringLiteral)
        assert branch.body[0].value == "positive"

    def test_if_else(self):
        result = parse('if x > 0\n  "positive"\nelse\n  "negative"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 1
        assert node.else_body is not None
        assert len(node.else_body) == 1
        assert isinstance(node.else_body[0], StringLiteral)
        assert node.else_body[0].value == "negative"

    def test_if_elif_else(self):
        result = parse('if x > 0\n  "positive"\nelif x == 0\n  "zero"\nelse\n  "negative"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 2
        assert node.branches[0].condition.operator == ">"
        assert isinstance(node.branches[0].body[0], StringLiteral)
        assert node.branches[0].body[0].value == "positive"
        assert node.branches[1].condition.operator == "=="
        assert isinstance(node.branches[1].body[0], StringLiteral)
        assert node.branches[1].body[0].value == "zero"
        assert node.else_body is not None
        assert isinstance(node.else_body[0], StringLiteral)
        assert node.else_body[0].value == "negative"

    def test_multiple_elif(self):
        text = 'if x > 2\n  "a"\nelif x > 1\n  "b"\nelif x > 0\n  "c"\nelif x == 0\n  "d"\nelse\n  "e"'
        result = parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 4
        assert node.else_body is not None

    def test_nested_if(self):
        result = parse('if a\n  if b\n    "both"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        assert len(node.branches) == 1
        inner = node.branches[0].body[0]
        assert isinstance(inner, IfElse)
        assert len(inner.branches) == 1
        assert isinstance(inner.branches[0].body[0], StringLiteral)
        assert inner.branches[0].body[0].value == "both"

    def test_complex_condition(self):
        result = parse('if a > 0 && b < 10\n  "ok"')
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, IfElse)
        cond = node.branches[0].condition
        assert isinstance(cond, BinaryOp)
        assert cond.operator == "&&"
        assert isinstance(cond.left, BinaryOp)
        assert cond.left.operator == ">"
        assert isinstance(cond.right, BinaryOp)
        assert cond.right.operator == "<"


class TestForLoop:
    def test_simple(self):
        result = parse("for i in items\n  process(i)")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert isinstance(node.variable, Identifier)
        assert node.variable.name == "i"
        assert isinstance(node.iterable, Identifier)
        assert node.iterable.name == "items"
        assert len(node.body) == 1
        assert isinstance(node.body[0], FunctionCall)
        assert node.body[0].callee.name == "process"

    def test_function_call_iterable(self):
        result = parse("for i in range(10)\n  i")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert isinstance(node.iterable, FunctionCall)
        assert node.iterable.callee.name == "range"
        assert len(node.iterable.args) == 1
        assert isinstance(node.iterable.args[0], NumericLiteral)
        assert node.iterable.args[0].value == 10

    def test_nested_for(self):
        result = parse("for i in a\n  for j in b\n    i + j")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert node.variable.name == "i"
        assert len(node.body) == 1
        inner = node.body[0]
        assert isinstance(inner, ForLoop)
        assert inner.variable.name == "j"
        assert len(inner.body) == 1
        assert isinstance(inner.body[0], BinaryOp)
        assert inner.body[0].operator == "+"

    def test_multi_line_body(self):
        result = parse("for i in items\n  x := i + 1\n  print(x)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, ForLoop)
        assert len(node.body) == 2
        assert isinstance(node.body[0], Binding)
        assert node.body[0].target.name == "x"
        assert isinstance(node.body[1], FunctionCall)
        assert node.body[1].callee.name == "print"
