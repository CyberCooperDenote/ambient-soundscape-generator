"""OutputDriver protocol — every driver implements `write(job_id, audio) -> Path`."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np


class OutputDriver(Protocol):
    sample_rate: int

    def write(self, job_id: str, audio: np.ndarray) -> Path: ...
    def close(self) -> None: ...