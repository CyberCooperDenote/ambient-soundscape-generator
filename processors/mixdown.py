"""Mixdown processor — writes the latent audio to disk via the output driver."""

from __future__ import annotations

import logging

from soundscape_pipeline.job import Job
from drivers.file import FileDriver

log = logging.getLogger(__name__)


class Stage:
    name = "processors.mixdown"

    def __init__(self, output_dir: str = "renders", sample_rate: int = 48000) -> None:
        self.driver = FileDriver(output_dir=output_dir, sample_rate=sample_rate)

    def __call__(self, job: Job) -> Job:
        latent = job.artifacts.get("latent")
        if not latent or "audio" not in latent:
            job.fail(self.name, "no latent audio to mix down")
            return job
        path = self.driver.write(job.id, latent["audio"])
        job.artifacts["mixdown"] = {"path": str(path), "sample_rate": self.driver.sample_rate}
        log.info("job %s -> %s", job.id, path)
        return job