"""Job — the unit of work that flows through every stage.

A Job is immutable in shape but mutable in payload: stages append to
`artifacts` and update `state`. The pipeline never inspects a Job's
contents; it just hands them along.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class JobState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass(slots=True)
class Job:
    """A single soundscape generation request.

    Attributes:
        prompt: free-form user prompt, e.g. "rain on a tin roof, distant thunder".
        mood: optional mood tag, e.g. "calm", "tense", "melancholy".
        seed: RNG seed; if None, a fresh one is generated.
        duration_s: target length in seconds.
        state: current lifecycle state.
        artifacts: stage name -> stage output (np.ndarray, dict, path, ...).
        errors: list of (stage, message) tuples accumulated during the run.
        created_at: unix timestamp.
        id: stable job id (uuid4 hex).
    """

    prompt: str
    mood: str | None = None
    seed: int | None = None
    duration_s: float = 30.0
    state: JobState = JobState.PENDING
    artifacts: dict[str, Any] = field(default_factory=dict)
    errors: list[tuple[str, str]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def with_seed(self) -> "Job":
        if self.seed is None:
            self.seed = uuid.uuid4().int & 0x7FFFFFFF
        return self

    def fail(self, stage: str, message: str) -> None:
        self.errors.append((stage, message))
        self.state = JobState.FAILED