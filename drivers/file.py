"""FileDriver — writes audio to a WAV/FLAC file under `output_dir`."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import soundfile as sf

log = logging.getLogger(__name__)


class FileDriver:
    def __init__(
        self,
        output_dir: str = "renders",
        sample_rate: int = 48000,
        fmt: str = "WAV",
        subtype: str = "PCM_24",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = sample_rate
        self.fmt = fmt
        self.subtype = subtype

    def write(self, job_id: str, audio: np.ndarray) -> Path:
        audio = np.asarray(audio, dtype=np.float32).reshape(-1)
        peak = float(np.max(np.abs(audio))) or 1.0
        if peak > 1.0:
            audio = audio / peak
        path = self.output_dir / f"{job_id}.{self.fmt.lower()}"
        sf.write(path, audio, self.sample_rate, subtype=self.subtype, format=self.fmt)
        return path

    def close(self) -> None:
        pass