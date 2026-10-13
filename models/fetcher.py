"""Download model weights listed in config/models.yaml.

Uses urllib so we don't drag in requests for a desktop tool. Progress is
rendered with rich if available.
"""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

from models.registry import ModelEntry, load_entries, verify

log = logging.getLogger(__name__)


def _