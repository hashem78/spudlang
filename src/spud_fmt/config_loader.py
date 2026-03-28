from pathlib import Path

import yaml

from spud_fmt.config import FmtConfig


def load_config(start: Path, config_path: Path | None = None) -> FmtConfig:
    """Load formatting config from a .spudfmt.yaml file.

    If ``config_path`` is given, reads that file directly.
    Otherwise, searches from ``start`` upward for ``.spudfmt.yaml``.
    Returns default config if no file is found.
    """
    if config_path is not None:
        return _read_config(config_path)

    current = start.resolve()
    if current.is_file():
        current = current.parent

    while True:
        candidate = current / ".spudfmt.yaml"
        if candidate.is_file():
            return _read_config(candidate)
        parent = current.parent
        if parent == current:
            break
        current = parent

    return FmtConfig()


def _read_config(path: Path) -> FmtConfig:
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return FmtConfig(**data)
