from __future__ import annotations

import math
import os
import shutil
import unittest
import uuid
from contextlib import contextmanager
from datetime import datetime
from collections.abc import Iterator
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from timewarp_file.timestamp import collect_targets, parse_user_datetime, set_modified_time

TEST_TEMP_ROOT = ROOT / "tmp" / "tests"


@contextmanager
def temporary_workspace() -> Iterator[Path]:
    TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    workspace = TEST_TEMP_ROOT / f"case-{uuid.uuid4().hex}"
    workspace.mkdir()
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


class TimestampTests(unittest.TestCase):
    def test_parse_iso_datetime(self) -> None:
        timestamp = parse_user_datetime("2026-05-15 18:30:00")
        parsed = datetime.fromtimestamp(timestamp)

        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 5)
        self.assertEqual(parsed.day, 15)
        self.assertEqual(parsed.hour, 18)
        self.assertEqual(parsed.minute, 30)

    def test_parse_slash_separated_iso_date(self) -> None:
        timestamp = parse_user_datetime("2026/05/15 18:30")
        parsed = datetime.fromtimestamp(timestamp)

        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 5)
        self.assertEqual(parsed.day, 15)
        self.assertEqual(parsed.hour, 18)
        self.assertEqual(parsed.minute, 30)

    def test_parse_today_shortcut_with_time(self) -> None:
        reference = datetime(2026, 5, 18, 14, 15)
        timestamp = parse_user_datetime("today 18:30", now=reference)
        parsed = datetime.fromtimestamp(timestamp)

        self.assertEqual(parsed, datetime(2026, 5, 18, 18, 30))

    def test_parse_tomorrow_shortcut_with_time(self) -> None:
        reference = datetime(2026, 5, 18, 14, 15)
        timestamp = parse_user_datetime("tomorrow 09:00", now=reference)
        parsed = datetime.fromtimestamp(timestamp)

        self.assertEqual(parsed, datetime(2026, 5, 19, 9, 0))

    def test_parse_yesterday_shortcut_without_time_uses_midnight(self) -> None:
        reference = datetime(2026, 5, 18, 14, 15)
        timestamp = parse_user_datetime("yesterday", now=reference)
        parsed = datetime.fromtimestamp(timestamp)

        self.assertEqual(parsed, datetime(2026, 5, 17, 0, 0))

    def test_parse_time_only_uses_today(self) -> None:
        reference = datetime(2026, 5, 18, 14, 15)
        timestamp = parse_user_datetime("6:45pm", now=reference)
        parsed = datetime.fromtimestamp(timestamp)

        self.assertEqual(parsed, datetime(2026, 5, 18, 18, 45))

    def test_set_modified_time_preserves_access_time(self) -> None:
        with temporary_workspace() as temp_dir:
            target = temp_dir / "example.txt"
            target.write_text("hello", encoding="utf-8")
            original_access_time = target.stat().st_atime
            desired = parse_user_datetime("2026-05-15 18:30:00")

            update = set_modified_time(target, desired)

            self.assertEqual(update.path, target)
            self.assertAlmostEqual(target.stat().st_atime, original_access_time, delta=2)
            self.assertAlmostEqual(target.stat().st_mtime, desired, delta=2)

    def test_collect_targets_recursively_sets_root_last(self) -> None:
        with temporary_workspace() as temp_dir:
            root = temp_dir
            child_dir = root / "child"
            child_dir.mkdir()
            child_file = child_dir / "example.txt"
            child_file.write_text("hello", encoding="utf-8")

            targets = collect_targets(root, recursive=True)

            self.assertIn(child_file.resolve(), targets)
            self.assertIn(child_dir.resolve(), targets)
            self.assertEqual(targets[-1], root.resolve())

    def test_collect_targets_accepts_quoted_paths(self) -> None:
        with temporary_workspace() as temp_dir:
            target = temp_dir / "example.txt"
            target.write_text("hello", encoding="utf-8")

            targets = collect_targets(f'"{target}"')

            self.assertEqual(targets, [target.resolve()])

    def test_collect_targets_rejects_blank_paths(self) -> None:
        with self.assertRaises(ValueError):
            collect_targets("   ")

    def test_collect_targets_recursively_uses_stable_order(self) -> None:
        with temporary_workspace() as temp_dir:
            root = temp_dir
            alpha_dir = root / "alpha"
            alpha_dir.mkdir()
            alpha_file = alpha_dir / "file.txt"
            alpha_file.write_text("alpha", encoding="utf-8")
            beta_file = root / "beta.txt"
            beta_file.write_text("beta", encoding="utf-8")

            targets = collect_targets(root, recursive=True)

            self.assertEqual(
                targets,
                [
                    alpha_file.resolve(),
                    alpha_dir.resolve(),
                    beta_file.resolve(),
                    root.resolve(),
                ],
            )

    def test_dry_run_does_not_touch_file(self) -> None:
        with temporary_workspace() as temp_dir:
            target = temp_dir / "example.txt"
            target.write_text("hello", encoding="utf-8")
            before = os.stat(target).st_mtime
            desired = parse_user_datetime("2026-05-15 18:30:00")

            update = set_modified_time(target, desired, dry_run=True)

            self.assertEqual(update.after_modified, desired)
            self.assertEqual(os.stat(target).st_mtime, before)

    def test_set_modified_time_rejects_non_finite_timestamp(self) -> None:
        with temporary_workspace() as temp_dir:
            target = temp_dir / "example.txt"
            target.write_text("hello", encoding="utf-8")

            with self.assertRaises(ValueError):
                set_modified_time(target, math.inf)


if __name__ == "__main__":
    unittest.main()
