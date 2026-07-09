from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from dev_scout.util import project_root, read_json, runs_dir, write_json


STAGE_DIRS = [
    "00-intake",
    "01-research/discover",
    "01-research/raw",
    "01-research/extracted",
    "01-research/lenses",
    "02-synthesize",
    "03-rank",
    "04-judge",
    "05-report",
    "06-email",
    "07-learning",
]


@dataclass
class RunContext:
    day: str
    root: Path = field(default_factory=runs_dir)

    @property
    def run_dir(self) -> Path:
        return self.root / self.day

    def ensure_layout(self) -> None:
        for rel in STAGE_DIRS:
            (self.run_dir / rel).mkdir(parents=True, exist_ok=True)

    def stage_path(self, stage: str) -> Path:
        return self.run_dir / stage

    def research_path(self, *parts: str) -> Path:
        base = self.run_dir / "01-research"
        for part in parts:
            base = base / part
        return base

    def load_manifest(self) -> dict:
        return read_json(self.run_dir / "run.manifest.json")

    def save_manifest(self, payload: dict) -> None:
        write_json(self.run_dir / "run.manifest.json", payload)

    def goal_path(self) -> Path:
        return self.run_dir / "GOAL.md"

    @staticmethod
    def from_day(day: str | None = None) -> RunContext:
        from dev_scout.models.jam import current_run_day

        return RunContext(day=day or current_run_day())

    @staticmethod
    def fixture_root() -> Path:
        return project_root() / "tests" / "fixtures"
