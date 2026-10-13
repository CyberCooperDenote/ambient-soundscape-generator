"""Spectral processor — builds a target magnitude spectrum from prompt+mood.

This stage produces a coarse spectral envelope (per-band energy target) that
the latent processor will match. It is cheap and deterministic, which makes
it useful for debugging the rest of the pipeline without loading a model.
"""

from __future__ import annotations

import logging

import numpy as np

from soundscape_pipeline.job import Job

log = logging.getLogger(__name__)

BANDS = 64  # log-spaced bands from 20 Hz to 20 kHz


def _log_bands(n: int, f_lo: float = 20.0, f_hi: float = 20000.0) -> np.ndarray:
    return np.geomspace(f_lo, f_hi, n, dtype=np.float64)


class Stage:
    name = "processors.spectral"

    def __init__(self, bands: int = BANDS, tilt_db_per_oct: float = -3.0) -> None:
        self.bands = bands
        self.tilt = tilt_db_per_oct

    def __call__(self, job: Job) -> Job:
        mood = job.artifacts.get("mood", {}).get("vector", [0.0, 0.0, 0.0, 0.0])
        _, _, density, brightness = mood

        freqs = _log_bands(self.bands)
        # Pink-ish base tilt, then mood-driven tilt adjustment.
        octaves = np.log2(freqs / freqs[0])
        tilt = self.tilt + 1.5 * brightness
        envelope_db = tilt * octaves

        # Density widens the mid-band bump.
        mid = np.exp(-((np.log2(freqs) - np.log2(800.0)) ** 2) / (0.6 + 0.4 * density))
        envelope_db = envelope_db + 6.0 * density * mid

        # Normalize to 0 dB peak.
        envelope_db = envelope_db - envelope_db.max()
        linear = np.power(10.0, envelope_db / 20.0)

        job.artifacts["spectral"] = {
            "freqs_hz": freqs.tolist(),
            "envelope_linear": linear.tolist(),
            "tilt_db_per_oct": float(tilt),
        }
        log.debug("spectral envelope built for job %s (%d bands)", job.id, self.bands)
        return job