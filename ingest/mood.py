"""Mood ingest stage — maps a mood tag to a small control vector.

The vector is later consumed by the latent processor to bias the sampler.
Values are in [-1, 1] per axis: valence, arousal, density, brightness.
"""

from __future__ import annotations

import logging

from soundscape_pipeline.job import Job

log = logging.getLogger(__name__)

# Hand-tuned anchors. Anything unknown falls back to neutral.
_MOODS: dict[str, tuple[float, float, float, float]] = {
    "calm":        ( 0.5, -0.6, -0.3, -0.2),
    "tense":       (-0.6,  0.7,  0.4,  0.3),
    "melancholy":  (-0.4, -0.3,  0.1, -0.5),
    "bright":      ( 0.7,  0.4,  0.2,  0.8),
    "cavernous":   ( 0.0, -0.2,  0.6, -0.4),
    "storm":       (-0.3,  0.9,  0.8,  0.1),
    "neutral":     ( 0.0,  0.0,  0.0,  0.0),
}


class Stage:
    name = "ingest.mood"

    def __init__(self, default: str = "neutral") -> None:
        self.default = default

    def __call__(self, job: Job) -> Job:
        tag = (job.mood or self.default).strip().lower()
        vec = _MOODS.get(tag)
        if vec is None:
            log.info("unknown mood %r, using neutral", tag)
            tag, vec = "neutral", _MOODS["neutral"]
        job.artifacts["mood"] = {
            "tag": tag,
            "vector": list(vec),
            "axes": ["valence", "arousal", "density", "brightness"],
        }
        return job