"""Pipeline — runs a Job through an ordered list of stages.

Stages are callables with signature `process(job: Job) -> Job`. The pipeline
is synchronous by default; `run_parallel` fans out independent jobs across
a worker pool. A single Job is always processed serially — stages may
depend on earlier artifacts.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, Sequence

from soundscape_pipeline.job import Job, JobState

Stage = Callable[[Job], Job]
log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, stages: Sequence[Stage], name: str = "default") -> None:
        if not stages:
            raise ValueError("Pipeline requires at least one stage")
        self.stages: list[Stage] = list(stages)
        self.name = name

    def run(self, job: Job) -> Job:
        job.state = JobState.RUNNING
        for stage in self.stages:
            stage_name = getattr(stage, "__name__", stage.__class__.__name__)
            try:
                job = stage(job)
            except Exception as exc:  # noqa: BLE001 — stage boundary
                log.exception("stage %s failed on job %s", stage_name, job.id)
                job.fail(stage_name, str(exc))
                return job
            if job.state is JobState.FAILED:
                return job
        job.state = JobState.DONE
        return job

    def run_parallel(self, jobs: Iterable[Job], max_workers: int = 4) -> list[Job]:
        results: list[Job] = []
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(self.run, j): j for j in jobs}
            for fut in as_completed(futures):
                results.append(fut.result())
        return results