# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
"""Friendly Windows launcher for TimeWarp File."""

from __future__ import annotations

from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from timewarp_file.cli import BANNER, CREDITS_BANNER, ask_yes_no, read_prompt
from timewarp_file.console import Style, clear_screen
from timewarp_file.timestamp import (
    collect_targets,
    format_local_timestamp,
    normalize_path,
    parse_user_datetime,
    set_modified_time,
)


SUCCESS_BANNER = r"""
     _____ _                __        __                  ____             _      
    |_   _(_)_ __ ___   ___ \ \      / /_ _ _ __ _ __    |  _ \ ___  __ _| |_   _ 
      | | | | '_ ` _ \ / _ \ \ \ /\ / / _` | '__| '_ \   | |_) / _ \/ _` | | | | |
      | | | | | | | | |  __/  \ V  V / (_| | |  | |_) |  |  _ <  __/ (_| | | |_| |
      |_| |_|_| |_| |_|\___|   \_/\_/ \__,_|_|  | .__/   |_| \_\___|\__,_|_|\__, |
                                                |_|                          |___/ 
"""

STOP_BANNER = r"""
     _____ _                __        __                  ____  _                 _ 
    |_   _(_)_ __ ___   ___ \ \      / /_ _ _ __ _ __    / ___|| | ___  ___  ___| |
      | | | | '_ ` _ \ / _ \ \ \ /\ / / _` | '__| '_ \   \___ \| |/ _ \/ __|/ _ \ |
      | | | | | | | | |  __/  \ V  V / (_| | |  | |_) |   ___) | | (_) \__ \  __/_|
      |_| |_|_| |_| |_|\___|   \_/\_/ \__,_|_|  | .__/   |____/|_|\___/|___/\___(_)
                                                |_|                                  
"""


def pause() -> None:
    input("\nPress Enter to return to the launcher...")


def choose_path() -> str:
    return read_prompt("Drag/drop or paste file/folder path: ").strip().strip('"')


def choose_time() -> str:
    print("\nExamples: 2026-05-15 18:30:00 | 2026-05-15 18:30 | now")
    return read_prompt("New modified time: ").strip()


def run_timewarp(dry_run: bool) -> int:
    style = Style()

    try:
        path = choose_path()
        time_value = choose_time()
        desired_timestamp = parse_user_datetime(time_value)
        root = normalize_path(path)
        recursive = root.is_dir() and ask_yes_no("Update everything inside this folder too?")
        targets = collect_targets(path, recursive=recursive)
    except (OSError, ValueError) as exc:
        print(style.red(f"\n[ERROR] {exc}"))
        pause()
        return 1

    print(style.cyan("\n[ TIME CORE ] Target scan complete"))
    print(style.white(f"Target time: {format_local_timestamp(desired_timestamp)}"))
    print(style.white(f"Mode: {'dry run preview' if dry_run else 'apply changes'}"))
    print(style.white(f"Items: {len(targets)}\n"))

    changed = 0
    failed = 0
    for target in targets:
        try:
            update = set_modified_time(target, desired_timestamp, dry_run=dry_run)
        except OSError as exc:
            failed += 1
            print(style.red(f"[FAIL] {target} - {exc}"))
            continue

        changed += 1
        before = format_local_timestamp(update.before_modified)
        after = format_local_timestamp(update.after_modified)
        status = style.yellow("[DRY]") if dry_run else style.green("[ OK]")
        print(f"{status} {target}")
        print(style.dim(f"      {before} -> {after}"))

    print()
    if failed:
        print(style.yellow(f"Done with warnings: {changed} changed, {failed} failed."))
        pause()
        return 2

    clear_screen()
    print(style.green(SUCCESS_BANNER))
    action = "would be updated" if dry_run else "updated"
    print(style.green(f"TimeWarp complete. {changed} item(s) {action}."))
    pause()
    return 0


def show_launcher() -> None:
    style = Style()
    clear_screen()
    print(style.cyan(BANNER))
    print(style.magenta(CREDITS_BANNER))
    print(style.cyan("        [ LAUNCHER   ]  Choose an action below\n"))
    print(style.white("        1. Change a file/folder timestamp"))
    print(style.white("        2. Dry-run preview"))
    print(style.white("        3. Help"))
    print(style.white("        4. Exit\n"))


def show_help() -> None:
    style = Style()
    clear_screen()
    print(style.cyan(BANNER))
    print(style.white("        Paste a file or folder path, then enter the date/time you want."))
    print(style.white("        Recommended format: 2026-05-15 18:30:00"))
    print(style.white("        Type 'now' to use the current time."))
    print(style.white("        Dry-run mode previews changes without touching timestamps."))
    pause()


def main() -> int:
    style = Style()

    while True:
        show_launcher()
        choice = read_prompt("Select option: ").strip().lower()

        if choice in {"1", "change", "start"}:
            return run_timewarp(dry_run=False)
        if choice in {"2", "dry", "preview"}:
            return run_timewarp(dry_run=True)
        if choice in {"3", "h", "help"}:
            show_help()
            continue
        if choice in {"4", "exit", "quit", "q"}:
            clear_screen()
            print(style.yellow(STOP_BANNER))
            print(style.yellow("TimeWarp launcher closed."))
            time.sleep(1)
            return 0

        print(style.red("Unknown option. Choose 1, 2, 3, or 4."))
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
