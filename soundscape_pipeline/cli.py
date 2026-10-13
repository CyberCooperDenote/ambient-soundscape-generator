"""Typer CLI — `asg generate`, `asg fetch-models`, `asg devices`."""

from __future__ import annotations

import logging
from pathlib import Path

import typer
import yaml
from rich.console import Console

from soundscape_pipeline.job import Job
from soundscape_pipeline.registry import build_default_pipeline
from utils.logging_setup import configure_logging

app = typer.Typer(help="AI ambient soundscape generator", no_args_is_help=True)
console = Console()


def _load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="e.g. 'rain on a tin roof, distant thunder'"),
    mood: str | None = typer.Option(None, "--mood", "-m"),
    duration: float = typer.Option(30.0, "--duration", "-d", help="seconds"),
    seed: int | None = typer.Option(None, "--seed", "-s"),
    config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c"),
) -> None:
    """Generate a soundscape from a prompt."""
    cfg = _load_config(config)
    configure_logging(cfg.get("logging", {}))
    pipeline = build_default_pipeline(cfg)
    job = Job(prompt=prompt, mood=mood, duration_s=duration, seed=seed).with_seed()
    console.print(f"[bold cyan]job[/] {job.id} seed={job.seed}")
    result = pipeline.run(job)
    if result.errors:
        for stage, msg in result.errors:
            console.print(f"[red]{stage}:[/] {msg}")
        raise typer.Exit(code=1)
    out = result.artifacts.get("mixdown", {}).get("path", "<no output>")
    console.print(f"[green]done[/] -> {out}")


@app.command("fetch-models")
def fetch_models(config: Path = typer.Option(Path("config/models.yaml"), "--config", "-c")) -> None:
    """Download model weights listed in the registry."""
    from models.fetcher import fetch_all

    cfg = _load_config(config)
    fetch_all(cfg.get("entries", []), console=console)


@app.command()
def devices() -> None:
    """List audio output devices."""
    import sounddevice as sd

    for idx, dev in enumerate(sd.query_devices()):
        if dev["max_output_channels"] > 0:
            console.print(f"{idx:>3}  {dev['name']}  ({dev['default_samplerate']:.0f} Hz)")


if __name__ == "__main__":
    app()