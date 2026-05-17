"""Timestamp parsing and file metadata helpers."""

from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SUPPORTED_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
)


@dataclass(frozen=True)
class TimestampUpdate:
    """Result of a timestamp update."""

    path: Path
    before_modified: float
    after_modified: float


def parse_user_datetime(value: str | None) -> float:
    """Parse a user supplied datetime into a Unix timestamp."""
    if value is None or not value.strip():
        raise ValueError("A desired time is required.")

    normalized = value.strip()
    if normalized.lower() == "now":
        return time.time()

    iso_candidate = normalized.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso_candidate)
    except ValueError:
        parsed = None

    if parsed is None:
        for date_format in SUPPORTED_FORMATS:
            try:
                parsed = datetime.strptime(normalized, date_format)
                break
            except ValueError:
                continue

    if parsed is None:
        examples = '"2026-05-15 18:30:00", "2026-05-15T18:30:00", or "now"'
        raise ValueError(f"Unsupported time format. Try {examples}.")

    if parsed.tzinfo is not None:
        return parsed.timestamp()

    return time.mktime(parsed.timetuple()) + (parsed.microsecond / 1_000_000)


def normalize_path(path_value: str | os.PathLike[str]) -> Path:
    """Turn a user supplied path into an expanded Path object."""
    path_text = os.fspath(path_value).strip()
    if not path_text:
        raise ValueError("A file or folder path is required.")

    if len(path_text) >= 2 and path_text[0] == path_text[-1] and path_text[0] in {"'", '"'}:
        path_text = path_text[1:-1].strip()

    if not path_text:
        raise ValueError("A file or folder path is required.")

    return Path(path_text).expanduser()


def _sort_key(path: Path) -> tuple[str, str]:
    return (path.name.casefold(), path.name)


def _collect_recursive_targets(root: Path) -> list[Path]:
    targets: list[Path] = []
    children = sorted(root.iterdir(), key=_sort_key)

    for child in children:
        if child.is_dir() and not child.is_symlink():
            targets.extend(_collect_recursive_targets(child))
        targets.append(child.resolve())

    return targets


def collect_targets(path_value: str | os.PathLike[str], recursive: bool = False) -> list[Path]:
    """Collect the file/folder targets that should receive the new modified time."""
    root = normalize_path(path_value)
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    root = root.resolve()
    if not recursive or not root.is_dir():
        return [root]

    targets = _collect_recursive_targets(root)
    targets.append(root)
    return targets


def set_modified_time(path: Path, timestamp: float, dry_run: bool = False) -> TimestampUpdate:
    """Set a path's modified time while preserving its current access time."""
    if not math.isfinite(timestamp):
        raise ValueError("Timestamp must be a finite number.")

    stat_result = path.stat()
    before_modified = stat_result.st_mtime

    if not dry_run:
        os.utime(path, (stat_result.st_atime, timestamp))
        after_modified = path.stat().st_mtime
    else:
        after_modified = timestamp

    return TimestampUpdate(
        path=path,
        before_modified=before_modified,
        after_modified=after_modified,
    )


def format_local_timestamp(timestamp: float) -> str:
    """Format a Unix timestamp using the user's local timezone."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
