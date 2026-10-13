"""WASAPI driver — real-time playback on Windows via sounddevice.

Falls back to a no-op on non-Windows so imports don't explode in CI.
"""

from __future__ import annotations

import logging
import sys

import numpy as np

log = logging.getLogger(__name__)

_IS_WINDOWS = sys.platform.startswith("win")


class WasapiDriver:
    def __init__(
        self,
        sample_rate: int = 48000,
        channels: int = 2,
        device_name: str | None = None,
        exclusive: bool = False,
        blocksize: int = 1024,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_name = device_name
        self.exclusive = exclusive
        self.blocksize = blocksize

    def play(self, audio: np.ndarray) -> None:
        if not _IS_WINDOWS:
            log.warning("WasapiDriver.play called on non-Windows; skipping")
            return
        import sounddevice as sd

        mono = np.asarray(audio, dtype=np.float32).reshape(-1)
        if self.channels == 2:
            mono = np.column_stack([mono, mono])
        device = self.device_name
        sd.play(mono, samplerate=self.sample_rate, device=device, blocking=True)
        sd.wait()

    def write(self, job_id: str, audio: np.ndarray):  # pragma: no cover — realtime only
        self.play(audio)
        from pathlib import Path

        return Path(f"<wasapi:{job_id}>")

    def close(self) -> None:
        pass