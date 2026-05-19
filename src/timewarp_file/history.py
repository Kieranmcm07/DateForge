# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
"""Persistent DateForge history and undo support."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .timestamp import TimestampUpdate, set_path_times


HISTORY_ENV = "DATEFORGE_HISTORY_PATH"


@dataclass(frozen=True)
class UndoFailure:
    """A path that could not be restored during undo."""

    path: Path
    error: Exception


@dataclass(frozen=True)
class UndoResult:
    """Result of an undo attempt."""

    original_entry: dict[str, Any]
    undo_entry: dict[str, Any] | None
    updates: list[TimestampUpdate]
    failures: list[UndoFailure]


class HistoryError(ValueError):
    """Raised when history cannot satisfy a requested operation."""


def _data_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "DateForge"
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "dateforge"
    return Path.home() / ".local" / "share" / "dateforge"


def history_path() -> Path:
    override = os.environ.get(HISTORY_ENV)
    if override:
        return Path(override).expanduser()
    return _data_dir() / "history.jsonl"


def load_history(path: Path | None = None) -> list[dict[str, Any]]:
    target = path or history_path()
    if not target.exists():
        return []

    entries: list[dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            entry = json.loads(text)
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def append_history(entry: dict[str, Any], path: Path | None = None) -> None:
    target = path or history_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        json.dump(entry, handle, sort_keys=True)
        handle.write("\n")


def _change_from_update(update: TimestampUpdate) -> dict[str, Any]:
    return {
        "path": str(update.path),
        "before_modified": update.before_modified,
        "after_modified": update.after_modified,
        "before_created": update.before_created,
        "after_created": update.after_created,
        "modified_requested": update.modified_requested,
        "created_requested": update.created_requested,
    }


def record_apply(updates: list[TimestampUpdate], path: Path | None = None) -> dict[str, Any]:
    entry = {
        "id": uuid.uuid4().hex,
        "action": "apply",
        "run_at": time.time(),
        "changes": [_change_from_update(update) for update in updates],
    }
    append_history(entry, path)
    return entry


def record_undo(
    original_entry: dict[str, Any],
    updates: list[TimestampUpdate],
    path: Path | None = None,
) -> dict[str, Any]:
    entry = {
        "id": uuid.uuid4().hex,
        "action": "undo",
        "undo_of": original_entry.get("id"),
        "run_at": time.time(),
        "changes": [_change_from_update(update) for update in updates],
    }
    append_history(entry, path)
    return entry


def last_undoable_entry(path: Path | None = None) -> dict[str, Any] | None:
    entries = load_history(path)
    undone_ids = {
        str(entry.get("undo_of"))
        for entry in entries
        if entry.get("action") == "undo" and entry.get("undo_of")
    }

    for entry in reversed(entries):
        entry_id = str(entry.get("id"))
        if entry.get("action") == "apply" and entry_id not in undone_ids:
            return entry
    return None


def undo_last_change(path: Path | None = None) -> UndoResult:
    entry = last_undoable_entry(path)
    if entry is None:
        raise HistoryError("No unapplied DateForge changes were found in history.")

    updates: list[TimestampUpdate] = []
    failures: list[UndoFailure] = []
    for change in entry.get("changes", []):
        target = Path(str(change.get("path", "")))
        modified_timestamp = (
            float(change["before_modified"])
            if change.get("modified_requested", True) and change.get("before_modified") is not None
            else None
        )
        created_timestamp = (
            float(change["before_created"])
            if change.get("created_requested") and change.get("before_created") is not None
            else None
        )

        try:
            update = set_path_times(
                target,
                modified_timestamp=modified_timestamp,
                created_timestamp=created_timestamp,
            )
        except (OSError, ValueError) as exc:
            failures.append(UndoFailure(target, exc))
            continue

        updates.append(update)

    undo_entry = None
    if not failures:
        undo_entry = record_undo(entry, updates, path)

    return UndoResult(entry, undo_entry, updates, failures)
