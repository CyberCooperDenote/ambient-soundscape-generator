"""Stage registry — maps config stage strings to callables.

Config uses dotted paths like "processors.spectral". We resolve them to
classes that expose `process(job) -> job`, instantiate with kwargs from
config, and hand the pipeline a flat list.
"""

from __future__ import annotations

import importlib
import logging
from typing import Any, Sequence

from soundscape_pipeline.pipeline import Pipeline, Stage

log = logging.getLogger(__name__)


def _resolve(dotted: str) -> Any:
    module_path, _, attr = dotted.rpartition(".")
    if not module_path:
        raise ValueError(f"stage path must be dotted, got {dotted!r}")
    # Try both `processors.spectral` (module) and `processors.spectral.Stage` (attr).
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    except (ImportError, AttributeError):
        mod = importlib.import_module(dotted)
        if not hasattr(mod, "Stage"):
            raise ValueError(f"module {dotted} has no Stage class") from None
        return mod.Stage


def build_stages(specs: Sequence[str | dict[str, Any]]) -> list[Stage]:
    stages: list[Stage] = []
    for spec in specs:
        if isinstance(spec, str):
            name, kwargs = spec, {}
        else:
            name, kwargs = next(iter(spec.items()))
        cls = _resolve(name)
        stages.append(cls(**kwargs))
    return stages


def build_default_pipeline(config: dict[str, Any]) -> Pipeline:
    specs = config.get("pipeline", {}).get("stages", [])
    stages = build_stages(specs)
    return Pipeline(stages, name="default")