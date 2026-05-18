"""Timestamp parsing and file metadata helpers."""

from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, time as datetime_time
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

TIME_ONLY_FORMATS = (
    "%H:%M:%S",
    "%H:%M",
    "%I:%M:%S %p",
    "%I:%M %p",
    "%I:%M%p",
    "%I %p",
    "%I%p",
)

RELATIVE_DATE_ALIASES = {
    "today": 0,
    "tomorrow": 1,
    "yesterday": -1,
}


@dataclass(frozen=True)
class TimestampUpdate:
    """Result of a timestamp update."""

    path: Path
    before_modified: float
    after_modified: float


def _to_local_timestamp(parsed: datetime) -> float:
    if parsed.tzinfo is not None:
        return parsed.timestamp()

    return time.mktime(parsed.timetuple()) + (parsed.microsecond / 1_000_000)


def _parse_time_of_day(value: str) -> datetime_time | None:
    time_text = " ".join(value.strip().split())
    if not time_text:
        return None

    lowered = time_text.lower()
    if lowered == "noon":
        return datetime_time(12, 0)
    if lowered == "midnight":
        return datetime_time(0, 0)

    for time_format in TIME_ONLY_FORMATS:
        for candidate in (time_text, time_text.upper()):
            try:
                return datetime.strptime(candidate, time_format).time()
            except ValueError:
                continue

    return None


def _parse_friendly_datetime(value: str, reference: datetime) -> datetime | None:
    collapsed = " ".join(value.strip().split())
    lowered = collapsed.lower()

    first_word, separator, rest = collapsed.partition(" ")
    date_offset = RELATIVE_DATE_ALIASES.get(first_word.lower())
    if date_offset is not None:
        target_date = (reference + timedelta(days=date_offset)).date()
        time_text = rest.strip()
        if time_text.lower().startswith("at "):
            time_text = time_text[3:].strip()

        parsed_time = _parse_time_of_day(time_text) if separator else datetime_time(0, 0)
        if parsed_time is None:
            return None
        return datetime.combine(target_date, parsed_time)

    parsed_time = _parse_time_of_day(lowered)
    if parsed_time is not None:
        return datetime.combine(reference.date(), parsed_time)

    return None


def parse_user_datetime(value: str | None, *, now: datetime | None = None) -> float:
    """Parse a user supplied datetime into a Unix timestamp."""
    if value is None or not value.strip():
        raise ValueError("A desired time is required.")

    reference = now or datetime.now()
    normalized = value.strip()
    if normalized.lower() == "now":
        if now is None:
            return time.time()
        return _to_local_timestamp(reference)

    friendly_parsed = _parse_friendly_datetime(normalized, reference)
    if friendly_parsed is not None:
        return _to_local_timestamp(friendly_parsed)

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
        examples = '"2026-05-15 18:30:00", "today 18:30", "tomorrow 09:00", or "now"'
        raise ValueError(f"Unsupported time format. Try {examples}.")

    return _to_local_timestamp(parsed)


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
