"""Latent processor — runs the ONNX latent model to synthesize raw audio.

Falls back to a procedural pink-noise generator if the model is missing, so
the pipeline is always runnable in a fresh checkout (`asg fetch-models` to
enable the real thing).
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from soundscape_pipeline.job import Job

log = logging.getLogger(__name__)


def _procedural(prompt: str, seed: int, duration_s: float, sr: int) -> np.ndarray:
    """Deterministic pink-ish noise shaped by the prompt hash."""
    rng = np.random.default_rng(seed)
    n = int(duration_s * sr)
    white = rng.standard_normal(n).astype(np.float32)

    # Simple 1/f shaping via cumulative filter.
    b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
    a = np.array([1.0, -2.494956002, 2.017265875, -0.522189400])
    from scipy.signal import lfilter

    pink = lfilter(b, a, white).astype(np.float32)
    peak = float(np.max(np.abs(pink))) or 1.0
    return pink / peak * 0.35


class Stage:
    name = "processors.latent"

    def __init__(
        self,
        model_path: str = "models/latent_ambient_v3.onnx",
        sample_rate: int = 48000,
        device: str = "cpu",
    ) -> None:
        self.model_path = Path(model_path)
        self.sample_rate = sample_rate
        self.device = device
        self._session = None

    def _load(self):
        if self._session is not None:
            return self._session
        if not self.model_path.exists():
            log.warning("latent model missing at %s, using procedural fallback", self.model_path)
            return None
        import onnxruntime as ort

        providers = ["CPUExecutionProvider"]
        if self.device == "cuda":
            providers.insert(0, "CUDAExecutionProvider")
        self._session = ort.InferenceSession(str(self.model_path), providers=providers)
        return self._session

    def __call__(self, job: Job) -> Job:
        mood = job.artifacts.get("mood", {}).get("vector", [0.0, 0.0, 0.0, 0.0])
        spectral = job.artifacts.get("spectral", {})
        session = self._load()

        if session is None:
            audio = _procedural(job.prompt, job.seed or 0, job.duration_s, self.sample_rate)
            job.artifacts["latent"] = {"audio": audio, "backend": "procedural"}
            return job

        n = int(job.duration_s * self.sample_rate)
        z = np.asarray(mood, dtype=np.float32).reshape(1, -1)
        env = np.asarray(spectral.get("envelope_linear", []), dtype=np.float32).reshape(1, -1)
        try:
            out = session.run(None, {"mood": z, "spectral": env, "length": np.array([n], dtype=np.int64)})
            audio = out[0].astype(np.float32).reshape(-1)[:n]
        except Exception as exc:  # noqa: BLE001 — model boundary
            log.exception("latent model failed, falling back to procedural: %s", exc)
            audio = _procedural(job.prompt, job.seed or 0, job.duration_s, self.sample_rate)
            job.artifacts["latent"] = {"audio": audio, "backend": "procedural"}
            return job

        job.artifacts["latent"] = {"audio": audio, "backend": "onnx"}
        return job