"""Prompt ingest stage — normalizes the user prompt and attaches a seed."""

from __future__ import annotations

import logging
import re

from soundscape_pipeline.job import Job

log = logging.getLogger(__name__)

_WS = re.compile(r"\s+")


class Stage:
    name = "ingest.prompt"

    def __init__(self, max_len: int = 400) -> None:
        self.max_len = max_len

    def __call__(self, job: Job) -> Job:
        text = _WS.sub(" ", job.prompt).strip()
        if not text:
            job.fail(self.name, "empty prompt")
            return job
        if len(text) > self.max_len:
            log.warning("prompt truncated from %d -> %d chars", len(text), self.max_len)
            text = text[: self.max_len]
        job.artifacts["prompt"] = {"text": text, "tokens": text.lower().split()}
        job.with_seed()
        return job