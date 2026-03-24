# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

import inspect

import structlog
from dependency_injector.wiring import PatchedCallable
from structlog.dev import (
    Column,
    ConsoleRenderer,
    KeyValueColumnFormatter,
)

RESET = "\033[0m"
LEVEL_STYLES = ConsoleRenderer.get_default_level_styles(colors=True)


class _LevelFormatter:
    def __call__(self, key: str, value: object) -> str:
        level = str(value)
        style = LEVEL_STYLES.get(level, "")
        return f"{style}[{level}]{RESET}"


def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            ConsoleRenderer(
                columns=[
                    Column(
                        "timestamp",
                        KeyValueColumnFormatter(
                            key_style=None,
                            value_style="",
                            reset_style="",
                            value_repr=str,
                        ),
                    ),
                    Column(
                        "level",
                        _LevelFormatter(),
                    ),
                    Column(
                        "scope",
                        KeyValueColumnFormatter(
                            key_style=None,
                            value_style="",
                            reset_style="",
                            value_repr=str,
                        ),
                    ),
                    Column(
                        "event",
                        KeyValueColumnFormatter(
                            key_style=None,
                            value_style="",
                            reset_style="",
                            value_repr=str,
                        ),
                    ),
                    Column(
                        "",
                        KeyValueColumnFormatter(
                            key_style="",
                            value_style="",
                            reset_style="",
                            value_repr=repr,
                        ),
                    ),
                ],
            ),
        ],
    )


_configure_structlog()


def _is_compiled() -> bool:
    return "__compiled__" in globals()


def create_logger() -> structlog.stdlib.BoundLogger:
    if _is_compiled():
        return structlog.get_logger(scope="spud")

    for frame_info in inspect.stack():
        patched = frame_info[0].f_locals.get("patched")
        if not isinstance(patched, PatchedCallable):
            continue
        fn = frame_info[0].f_locals.get("fn")
        args = frame_info[0].f_locals.get("args", ())
        if args and hasattr(args[0], "__class__"):
            scope = type(args[0]).__name__
        else:
            scope = fn.__name__  # ty:ignore[unresolved-attribute]
        return structlog.get_logger(scope=scope)
    return structlog.get_logger(scope="unknown")
