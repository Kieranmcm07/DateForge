# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
from __future__ import annotations

import os
import shutil
import sys
import unittest
import uuid
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from timewarp_file.cli import read_batch_paths
from timewarp_file.history import load_history, record_apply, undo_last_change
from timewarp_file.presets import delete_preset, load_presets, save_preset
from timewarp_file.timestamp import (
    collect_targets,
    get_created_time,
    parse_user_datetime,
    set_modified_time,
    set_path_times,
)

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


class FeatureTests(unittest.TestCase):
    def test_collect_targets_supports_include_and_exclude_filters(self) -> None:
        with temporary_workspace() as temp_dir:
            keep = temp_dir / "keep.txt"
            keep.write_text("keep", encoding="utf-8")
            skip = temp_dir / "skip.log"
            skip.write_text("skip", encoding="utf-8")
            nested = temp_dir / "nested"
            nested.mkdir()
            inner = nested / "inner.txt"
            inner.write_text("inner", encoding="utf-8")

            targets = collect_targets(
                temp_dir,
                recursive=True,
                include=["*.txt"],
                exclude=["inner.txt"],
            )

            self.assertEqual(targets, [keep.resolve()])

    def test_batch_paths_are_resolved_relative_to_batch_file(self) -> None:
        with temporary_workspace() as temp_dir:
            target = temp_dir / "target.txt"
            target.write_text("target", encoding="utf-8")
            batch_file = temp_dir / "targets.txt"
            batch_file.write_text("# comment\ntarget.txt\n\n", encoding="utf-8-sig")

            paths = read_batch_paths(str(batch_file))

            self.assertEqual(paths, [target])

    def test_presets_can_be_saved_loaded_and_deleted(self) -> None:
        with temporary_workspace() as temp_dir:
            presets_file = temp_dir / "presets.json"
            timestamp = parse_user_datetime("2026-05-15 18:30:00")

            saved_name = save_preset("Release", timestamp, presets_file)
            presets = load_presets(presets_file)
            deleted_name = delete_preset("release", presets_file)

            self.assertEqual(saved_name, "release")
            self.assertEqual(presets["release"], timestamp)
            self.assertEqual(deleted_name, "release")
            self.assertEqual(load_presets(presets_file), {})

    def test_history_undo_restores_last_modified_time(self) -> None:
        with temporary_workspace() as temp_dir:
            history_file = temp_dir / "history.jsonl"
            target = temp_dir / "example.txt"
            target.write_text("hello", encoding="utf-8")
            before = target.stat().st_mtime
            desired = parse_user_datetime("2026-05-15 18:30:00")

            update = set_modified_time(target, desired)
            record_apply([update], history_file)
            result = undo_last_change(history_file)

            self.assertFalse(result.failures)
            self.assertAlmostEqual(target.stat().st_mtime, before, delta=2)
            self.assertEqual([entry["action"] for entry in load_history(history_file)], ["apply", "undo"])

    @unittest.skipUnless(os.name == "nt", "created time updates are Windows-only")
    def test_set_path_times_can_update_created_time_on_windows(self) -> None:
        with temporary_workspace() as temp_dir:
            target = temp_dir / "example.txt"
            target.write_text("hello", encoding="utf-8")
            desired = parse_user_datetime("2026-05-15 18:30:00")

            update = set_path_times(target, created_timestamp=desired)

            self.assertTrue(update.created_requested)
            self.assertAlmostEqual(get_created_time(target), desired, delta=2)


if __name__ == "__main__":
    unittest.main()
