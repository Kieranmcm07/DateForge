# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
"""Friendly Windows launcher for DateForge."""

from __future__ import annotations

from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from timewarp_file.cli import (
    ask_yes_no,
    display_path,
    read_prompt,
    render_banner,
    render_credits,
    render_notice_lines,
)
from timewarp_file.console import Style, clear_screen
from timewarp_file.timestamp import (
    collect_targets,
    format_local_timestamp,
    normalize_path,
    parse_user_datetime,
    set_modified_time,
)


def pause() -> None:
    input("\nPress Enter to return to the launcher...")


def choose_path() -> str:
    return read_prompt("Drag/drop or paste file/folder path: ").strip().strip('"')


def choose_time() -> str:
    print("\nExamples: 2026-05-15 18:30:00 | today 18:30 | tomorrow 09:00 | now")
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

    colour = "yellow" if dry_run else "green"
    clear_screen()
    print(render_banner(style, "preview" if dry_run else "cli", colour))
    action = "TIMESTAMP PREVIEW READY" if dry_run else "TIMESTAMP WRITE ARMED"
    print()
    print(render_notice_lines(style, ["TARGET SCAN COMPLETE", action], colour))
    print()
    print(f"      Target time: {format_local_timestamp(desired_timestamp)}")
    print(f"      Mode: {'preview only' if dry_run else 'apply changes'}")
    print(f"      Items: {len(targets)}\n")

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
        label = f"[ {'PREVIEW' if dry_run else 'APPLY':<11} ]"
        status = style.yellow(label) if dry_run else style.green(label)
        print(f"      {status}  {display_path(target)}")
        print(f"                    {style.dim(before)} -> {style.white(after)}")

    print()
    if failed:
        action = "previewed" if dry_run else "changed"
        print(style.yellow(f"Done with warnings: {changed} {action}, {failed} failed."))
        pause()
        return 2

    clear_screen()
    print(render_banner(style, "preview" if dry_run else "complete", "yellow" if dry_run else "green"))
    print()
    print(render_notice_lines(style, ["TARGETS PROCESSED", "DATEFORGE COMPLETE"], "yellow" if dry_run else "green"))
    action = "would be updated" if dry_run else "updated"
    print(style.wrap(f"\n      DateForge complete. {changed} item(s) {action}.", "93" if dry_run else "92"))
    pause()
    return 0


def show_launcher() -> None:
    style = Style()
    clear_screen()
    print(render_banner(style, "launcher", "green"))
    print()
    print(render_notice_lines(style, ["ACCESS GRANTED", "DATEFORGE SYSTEM ONLINE"], "green"))
    print()
    print(style.green("      [ 01 ]  Change a file/folder timestamp"))
    print(style.green("      [ 02 ]  Dry-run preview"))
    print(style.green("      [ 03 ]  Help"))
    print(style.green("      [ 04 ]  Exit\n"))


def show_help() -> None:
    style = Style()
    clear_screen()
    print(render_banner(style, "help", "magenta"))
    print()
    print(style.magenta("      Paste a file or folder path, then enter the date/time you want."))
    print(style.magenta("      Recommended format: 2026-05-15 18:30:00"))
    print(style.magenta("      Easier shortcuts: now, today 18:30, tomorrow 09:00, yesterday."))
    print(style.magenta("      CLI safety flag: --dry-run previews changes without touching timestamps."))
    print()
    print(render_credits(style))
    pause()


def main() -> int:
    style = Style()

    while True:
        show_launcher()
        choice = read_prompt("Select option: ").strip().lower()

        if choice in {"1", "change", "start"}:
            run_timewarp(dry_run=False)
            continue
        if choice in {"2", "dry", "dry-run", "preview"}:
            run_timewarp(dry_run=True)
            continue
        if choice in {"3", "h", "help"}:
            show_help()
            continue
        if choice in {"4", "exit", "quit", "q"}:
            clear_screen()
            print(render_banner(style, "closed", "red"))
            print()
            print(render_notice_lines(style, ["SESSION TERMINATED", "DATEFORGE OFFLINE"], "red"))
            print(style.red("\n      DateForge launcher closed."))
            time.sleep(1)
            return 0

        print(style.red("      Unknown option. Choose 1, 2, 3, or 4."))
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
