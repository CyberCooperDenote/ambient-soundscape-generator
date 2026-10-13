"""ambient-soundscape-generator — pipeline core.

Public surface:
    from soundscape_pipeline import Pipeline, Job, build_default_pipeline
"""

from soundscape_pipeline.job import Job
from soundscape_pipeline.pipeline import Pipeline
from soundscape_pipeline.registry import build_default_pipeline

__all__ = ["Job", "Pipeline", "build_default_pipeline"]
__version__ = "0.6.3"