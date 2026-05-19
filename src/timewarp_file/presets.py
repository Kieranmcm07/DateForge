# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
"""Saved timestamp presets for DateForge."""

from __future__ import annotations

import json
import os
from pathlib import Path


PRESETS_ENV = "DATEFORGE_PRESETS_PATH"


def _data_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "DateForge"
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "dateforge"
    return Path.home() / ".local" / "share" / "dateforge"


def presets_path() -> Path:
    override = os.environ.get(PRESETS_ENV)
    if override:
        return Path(override).expanduser()
    return _data_dir() / "presets.json"


def normalize_preset_name(name: str) -> str:
    normalized = " ".join(name.strip().split())
    if not normalized:
        raise ValueError("Preset name is required.")
    return normalized.casefold()


def load_presets(path: Path | None = None) -> dict[str, float]:
    target = path or presets_path()
    if not target.exists():
        return {}

    with target.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        raise ValueError(f"Preset file is not valid: {target}")

    return {normalize_preset_name(str(name)): float(timestamp) for name, timestamp in raw.items()}


def write_presets(presets: dict[str, float], path: Path | None = None) -> None:
    target = path or presets_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(dict(sorted(presets.items())), handle, indent=2)
        handle.write("\n")


def save_preset(name: str, timestamp: float, path: Path | None = None) -> str:
    normalized = normalize_preset_name(name)
    presets = load_presets(path)
    presets[normalized] = timestamp
    write_presets(presets, path)
    return normalized


def delete_preset(name: str, path: Path | None = None) -> str:
    normalized = normalize_preset_name(name)
    presets = load_presets(path)
    if normalized not in presets:
        raise KeyError(normalized)
    del presets[normalized]
    write_presets(presets, path)
    return normalized


def get_preset(name: str, path: Path | None = None) -> float:
    normalized = normalize_preset_name(name)
    presets = load_presets(path)
    if normalized not in presets:
        raise KeyError(normalized)
    return presets[normalized]
