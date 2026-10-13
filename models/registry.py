"""Model registry — loads config/models.yaml, verifies hashes, returns paths."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ModelEntry:
    id: str
    task: str
    path: Path
    sha256: str
    url: str | None = None
    sample_rate: int = 48000


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            buf = fh.read(chunk)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def load_entries(raw: list[dict]) -> list[ModelEntry]:
    out: list[ModelEntry] = []
    for e in raw:
        out.append(
            ModelEntry(
                id=e["id"],
                task=e["task"],
                path=Path(e["path"]),
                sha256=e.get("sha256", ""),
                url=e.get("url"),
                sample_rate=int(e.get("sample_rate", 48000)),
            )
        )
    return out


def verify(entry: ModelEntry) -> bool:
    if not entry.path.exists():
        log.warning("model %s missing at %s", entry.id, entry.path)
        return False
    if not entry.sha256 or entry.sha256.startswith("REPLACE"):
        log.warning("model %s has no pinned hash; skipping verify", entry.id)
        return True
    actual = sha256_file(entry.path)
    if actual != entry.sha256:
        log.error("model %s hash mismatch: %s != %s", entry.id, actual, entry.sha256)
        return False
    return True