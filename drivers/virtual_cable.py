"""VirtualCable driver — streams audio into a named pipe for OBS/Voicemeeter.

Not a real device driver; it's a writer that hooks the VB-Audio Virtual
Cable (or any named-pipe consumer) already installed on the machine.
"""

from __future__ import annotations

import logging
import os
import sys

import numpy as np

log = logging.getLogger(__name__)

_DEFAULT_PIPE = r"\\.\pipe\ambient-soundscape-generator"


class VirtualCableDriver:
    def __init__(self, pipe_name: str = _DEFAULT_PIPE, sample_rate: int = 48000) -> None:
        self.pipe_name = pipe_name
        self.sample_rate = sample_rate

    def write(self, job_id: str, audio: np.ndarray):
        from pathlib import Path

        if not sys.platform.startswith("win"):
            log.warning("VirtualCableDriver only supported on Windows; skipping write")
            return Path(f"<vbc:{job_id}>")

        pcm = (np.asarray(audio, dtype=np.float32) * 32767.0).astype("<i2").tobytes()
        try:
            with open(self.pipe_name, "wb", buffering=0) as pipe:
                pipe.write(pcm)
        except OSError as exc:
            log.error("virtual cable write failed: %s", exc)
        return Path(f"<vbc:{job_id}>")

    def close(self) -> None:
        pass