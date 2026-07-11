from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    return project_root() / "config"


def system_memory_dir() -> Path:
    return project_root() / "system" / "memory"


def data_dir() -> Path:
    return project_root() / "data"


def runs_dir() -> Path:
    return project_root() / "runs"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return {}
    return data


def read_json(path: Path) -> Any:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_json_with_secret_allowlist(path: Path, payload: Any, secret_key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    lines = text.splitlines()
    marker = f'"{secret_key}": '
    for index, line in enumerate(lines):
        if marker not in line:
            continue
        stripped = line.rstrip()
        has_trailing_comma = stripped.endswith(",")
        if has_trailing_comma:
            stripped = stripped[:-1]
        allowlist = ', "// pragma: allowlist secret": ""'
        if has_trailing_comma:
            allowlist += ","
        lines[index] = f"{stripped}{allowlist}"
        break
    else:
        raise KeyError(f"Secret key '{secret_key}' not found in payload")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows
