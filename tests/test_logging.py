# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from dependency_injector.wiring import Provide, inject

from spud.di import Container
from spud.di.logging import LEVEL_STYLES, RESET, _LevelFormatter


@inject
def _injected_function(logger=Provide[Container.logger]):
    return logger


@inject
def _injected_alpha(logger=Provide[Container.logger]):
    return logger


@inject
def _injected_beta(logger=Provide[Container.logger]):
    return logger


class _ServiceA:
    @inject
    def __init__(self, logger=Provide[Container.logger]):
        self.logger = logger


class _ServiceB:
    @inject
    def __init__(self, logger=Provide[Container.logger]):
        self.logger = logger


class _ServiceWithMethod:
    @inject
    def do_work(self, logger=Provide[Container.logger]):
        return logger


class TestLevelFormatter:
    def test_known_level_applies_style(self):
        fmt = _LevelFormatter()
        result = fmt("level", "info")
        expected_style = LEVEL_STYLES["info"]
        assert result == f"{expected_style}info{RESET}"

    def test_unknown_level_no_style(self):
        fmt = _LevelFormatter()
        result = fmt("level", "nonexistent")
        assert result == f"nonexistent{RESET}"

    def test_all_standard_levels(self):
        fmt = _LevelFormatter()
        for level in ("debug", "info", "warning", "error", "critical"):
            result = fmt("level", level)
            assert LEVEL_STYLES[level] in result
            assert level in result
            assert result.endswith(RESET)


class TestCreateLoggerFunctionScope:
    def setup_method(self):
        self.container = Container()
        self.container.wire(modules=[__name__])

    def teardown_method(self):
        self.container.unwire()

    def test_function_scope(self):
        logger = _injected_function()
        assert logger._context["scope"] == "_injected_function"

    def test_different_function_names(self):
        assert _injected_alpha()._context["scope"] == "_injected_alpha"
        assert _injected_beta()._context["scope"] == "_injected_beta"


class TestCreateLoggerClassScope:
    def setup_method(self):
        self.container = Container()
        self.container.wire(modules=[__name__])

    def teardown_method(self):
        self.container.unwire()

    def test_constructor_injection_uses_class_name_not_init(self):
        svc = _ServiceA()
        assert svc.logger._context["scope"] == "_ServiceA"
        assert "__init__" not in svc.logger._context["scope"]

    def test_method_injection_uses_class_name_not_method(self):
        svc = _ServiceWithMethod()
        logger = svc.do_work()
        assert logger._context["scope"] == "_ServiceWithMethod"
        assert "do_work" not in logger._context["scope"]

    def test_different_classes(self):
        assert _ServiceA().logger._context["scope"] == "_ServiceA"
        assert _ServiceB().logger._context["scope"] == "_ServiceB"

    def test_logger_persists_scope_from_constructor(self):
        """Logger created in __init__ keeps its scope when used in other methods."""
        svc = _ServiceA()
        svc.logger.info("test")
        assert svc.logger._context["scope"] == "_ServiceA"


class TestCreateLoggerFallback:
    def test_no_injection_returns_unknown(self):
        from spud.di.logging import create_logger

        logger = create_logger()
        assert logger._context["scope"] == "unknown"


class TestLogOutput:
    def setup_method(self):
        self.container = Container()
        self.container.wire(modules=[__name__])

    def teardown_method(self):
        self.container.unwire()

    def test_output_contains_scope_and_message(self, capsys):
        logger = _injected_function()
        logger.info("test message")
        output = capsys.readouterr().out
        assert "_injected_function" in output
        assert "test message" in output
        assert "info" in output

    def test_output_has_no_brackets(self, capsys):
        logger = _injected_function()
        logger.info("hello")
        output = capsys.readouterr().out
        assert "[info" not in output
        assert "info]" not in output
