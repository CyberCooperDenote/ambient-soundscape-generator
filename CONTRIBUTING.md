# Contributing to ambient-soundscape-generator

Thanks for wanting to help build the fridge hum of the future. This repo is a
Python-first Windows desktop tool that generates ambient soundscapes from a
prompt, a mood tag, or a seed — using a pipeline/worker architecture so
generation stages can be swapped, profiled, and parallelized independently.

## Ground rules

- Python 3.11+ on Windows 10/11. Linux/macOS run in CI but the shipping target
  is Windows desktop (WASAPI + SoundDevice backends).
- One pipeline stage per PR where possible. Stages live in
  `soundscape_pipeline/stages/`.
- Every stage must expose `process(job: Job) -> Job`. No side channels.
- No blocking calls in the audio driver path. If it blocks, it belongs in a
  worker, not a driver.
- Tests: `pytest -q`. Coverage floor is 70% on `soundscape_pipeline/`.

## Repo shape

```
soundscape_pipeline/    core pipeline + stage implementations
ingest/                 request handlers that turn user input into Jobs
processors/             DSP + model inference processors
drivers/                output drivers (file, WASAPI, ASIO, virtual cable)
models/                 model wrappers + registry (weights are gitignored)
utils/                  job queue, ring buffer, logging, timers
config/                 YAML configs + schema
tests/                  pytest suites
```

## Style

- `ruff` + `black` (line length 100).
- Type hints everywhere except throwaway scripts.
- Logging via `utils.logging_setup.get_logger(__name__)` — no bare `print`.

## PR checklist

- [ ] Stage added under `soundscape_pipeline/stages/` with `process()`.
- [ ] Stage registered in `soundscape_pipeline/registry.py`.
- [ ] Unit test added or updated under `tests/`.
- [ ] Config default added to `config/default.yaml` if the stage is opt-in.
- [ ] `pytest -q` passes locally on Windows.

## Reporting bugs

Open an issue with: OS build, Python version, output device, the prompt or
seed used, and the full log at `logs/pipeline.log`.