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
    print_history,
    print_update,
    read_prompt,
    render_banner,
    render_credits,
    render_notice_lines,
    render_status_rows,
    render_terminal_prompt,
    resolve_timestamp_value,
)
from timewarp_file.console import Style, clear_screen
from timewarp_file.history import HistoryError, record_apply, undo_last_change
from timewarp_file.presets import delete_preset, load_presets, save_preset
from timewarp_file.timestamp import (
    collect_targets,
    format_local_timestamp,
    normalize_path,
    parse_user_datetime,
    set_path_times,
)


def pause() -> None:
    style = Style()
    input(style.grey("\nPress Enter to return to the DateForge console..."))


def choose_path() -> str:
    style = Style()
    return read_prompt(render_terminal_prompt(style, "target.path")).strip().strip('"')


def choose_time() -> str:
    style = Style()
    print(style.dim("\n      Examples: 2026-05-15 18:30:00 | today 18:30 | tomorrow 09:00 | now | preset name"))
    return read_prompt(render_terminal_prompt(style, "target.time")).strip()


def split_patterns(value: str) -> list[str]:
    return [pattern.strip() for pattern in value.split(",") if pattern.strip()]


def choose_filters(recursive: bool) -> tuple[list[str] | None, list[str] | None]:
    if not recursive:
        return None, None

    style = Style()
    include_text = read_prompt(style.cyan("Include only patterns, comma separated [blank for all]: ")).strip()
    exclude_text = read_prompt(style.cyan("Exclude patterns, comma separated [blank for none]: ")).strip()
    return split_patterns(include_text) or None, split_patterns(exclude_text) or None


def choose_created_time(modified_timestamp: float) -> float | None:
    if not ask_yes_no("Update Windows created time too?"):
        return None
    if ask_yes_no("Use the same timestamp for created time?", default=True):
        return modified_timestamp

    style = Style()
    created_value = read_prompt(render_terminal_prompt(style, "created.time")).strip()
    return resolve_timestamp_value(created_value)


def run_timewarp() -> int:
    style = Style()

    try:
        path = choose_path()
        time_value = choose_time()
        modified_timestamp = resolve_timestamp_value(time_value)
        created_timestamp = choose_created_time(modified_timestamp)
        root = normalize_path(path)
        recursive = root.is_dir() and ask_yes_no("Update everything inside this folder too?")
        include, exclude = choose_filters(recursive)
        targets = collect_targets(path, recursive=recursive, include=include, exclude=exclude)
        if not targets:
            raise ValueError("No targets matched the requested filter settings.")
    except (OSError, ValueError) as exc:
        print(style.red(f"\n      >>> ACCESS DENIED: {exc}"))
        pause()
        return 1

    clear_screen()
    print(render_banner(style, "cli", "green"))
    print()
    print(render_notice_lines(style, ["TARGET SCAN COMPLETE", "TIMESTAMP WRITE ARMED"], "green"))
    print()
    print(
        render_status_rows(
            style,
            [
                ("MODIFIED", format_local_timestamp(modified_timestamp)),
                *(
                    [("CREATED", format_local_timestamp(created_timestamp))]
                    if created_timestamp is not None
                    else []
                ),
                ("MODE", "apply changes"),
                ("ITEMS", str(len(targets))),
                *( [("INCLUDE", ", ".join(include))] if include else [] ),
                *( [("EXCLUDE", ", ".join(exclude))] if exclude else [] ),
            ],
            "green",
        )
    )
    print()

    updates = []
    failed = 0
    for target in targets:
        try:
            update = set_path_times(
                target,
                modified_timestamp=modified_timestamp,
                created_timestamp=created_timestamp,
            )
        except (OSError, ValueError) as exc:
            failed += 1
            print(style.red(f"[FAIL] {target} - {exc}"))
            continue

        updates.append(update)
        print_update(update, style)

    if updates:
        try:
            record_apply(updates)
        except OSError as exc:
            print(style.yellow(f"Warning: could not write history log: {exc}"))

    print()
    if failed:
        print(style.yellow(f"Done with warnings: {len(updates)} changed, {failed} failed."))
        pause()
        return 2

    clear_screen()
    print(render_banner(style, "complete", "green"))
    print()
    print(render_notice_lines(style, ["TARGETS PROCESSED", "DATEFORGE COMPLETE"], "green"))
    print(style.green(f"\n      DateForge complete. {len(updates)} item(s) updated."))
    pause()
    return 0


def run_undo() -> int:
    style = Style()
    clear_screen()
    print(render_banner(style, "cli", "cyan"))
    print()

    try:
        result = undo_last_change()
    except HistoryError as exc:
        print(style.red(f"      >>> UNDO BLOCKED: {exc}"))
        pause()
        return 1
    except (OSError, ValueError) as exc:
        print(style.red(f"      >>> UNDO FAILED: {exc}"))
        pause()
        return 1

    print(render_notice_lines(style, ["UNDO RESTORE COMPLETE"], "cyan"))
    print()
    for update in result.updates:
        print_update(update, style, "UNDO", "cyan")
    for failure in result.failures:
        print(style.red(f"[FAIL] {failure.path} - {failure.error}"))

    print()
    if result.failures:
        print(style.yellow(f"Undo finished with warnings: {len(result.updates)} restored, {len(result.failures)} failed."))
        pause()
        return 2

    print(style.green(f"Undo complete. {len(result.updates)} item(s) restored."))
    pause()
    return 0


def show_history() -> None:
    style = Style()
    clear_screen()
    print(render_banner(style, "cli", "blue"))
    print()
    print_history(style, 10)
    pause()


def show_presets() -> None:
    style = Style()

    while True:
        clear_screen()
        print(render_banner(style, "help", "magenta"))
        print()
        try:
            presets = load_presets()
        except (OSError, ValueError) as exc:
            print(style.red(f"      >>> PRESET STORE FAILED: {exc}"))
            pause()
            return

        if presets:
            print(render_notice_lines(style, ["SAVED PRESETS"], "magenta"))
            for name, timestamp in sorted(presets.items()):
                print(f"      {style.magenta(name)}  {format_local_timestamp(timestamp)}")
        else:
            print(style.yellow("      No presets saved yet."))

        print()
        print(style.cyan("      [ 01 ]  Save preset"))
        print(style.cyan("      [ 02 ]  Delete preset"))
        print(style.cyan("      [ 03 ]  Back\n"))
        choice = read_prompt(render_terminal_prompt(style, "presets")).strip().lower()

        if choice in {"1", "save"}:
            name = read_prompt(render_terminal_prompt(style, "preset.name")).strip()
            time_value = choose_time()
            try:
                timestamp = parse_user_datetime(time_value)
                saved_name = save_preset(name, timestamp)
            except (OSError, ValueError) as exc:
                print(style.red(f"      >>> PRESET FAILED: {exc}"))
            else:
                print(style.green(f"      >>> PRESET SAVED: {saved_name}"))
            time.sleep(1)
            continue

        if choice in {"2", "delete", "remove"}:
            name = read_prompt(render_terminal_prompt(style, "preset.name")).strip()
            try:
                deleted_name = delete_preset(name)
            except KeyError:
                print(style.red("      >>> PRESET NOT FOUND"))
            except (OSError, ValueError) as exc:
                print(style.red(f"      >>> PRESET FAILED: {exc}"))
            else:
                print(style.green(f"      >>> PRESET DELETED: {deleted_name}"))
            time.sleep(1)
            continue

        if choice in {"3", "back", "b"}:
            return

        print(style.red("      >>> UNKNOWN COMMAND. Choose 1, 2, or 3."))
        time.sleep(1)


def show_launcher() -> None:
    style = Style()
    clear_screen()
    print(render_banner(style, "launcher", "green"))
    print()
    print(render_notice_lines(style, ["ACCESS GRANTED", "DATEFORGE SYSTEM ONLINE"], "green"))
    print()
    print(style.cyan("      [ 01 ]  Forge timestamp"))
    print(style.cyan("      [ 02 ]  Undo last change"))
    print(style.cyan("      [ 03 ]  Presets"))
    print(style.cyan("      [ 04 ]  History log"))
    print(style.cyan("      [ 05 ]  Help node"))
    print(style.cyan("      [ 06 ]  Terminate session\n"))


def show_help() -> None:
    style = Style()
    clear_screen()
    print(render_banner(style, "help", "magenta"))
    print()
    print(
        render_status_rows(
            style,
            [
                ("PATH", "Paste or drag a file/folder path into the terminal"),
                ("FORMAT", "Recommended: 2026-05-15 18:30:00"),
                ("SHORTCUTS", "now, today 18:30, tomorrow 09:00, yesterday"),
                ("CREATED", "Windows created time can be updated too"),
                ("FILTERS", "Recursive updates can include/exclude globs"),
                ("UNDO", "History can restore the last DateForge change"),
            ],
            "magenta",
        )
    )
    print()
    print(render_credits(style))
    pause()


def main() -> int:
    style = Style()

    while True:
        show_launcher()
        choice = read_prompt(render_terminal_prompt(style, "dateforge")).strip().lower()

        if choice in {"1", "change", "start"}:
            run_timewarp()
            continue
        if choice in {"2", "undo"}:
            run_undo()
            continue
        if choice in {"3", "preset", "presets"}:
            show_presets()
            continue
        if choice in {"4", "history", "log"}:
            show_history()
            continue
        if choice in {"5", "h", "help"}:
            show_help()
            continue
        if choice in {"6", "exit", "quit", "q"}:
            clear_screen()
            print(render_banner(style, "closed", "red"))
            print()
            print(render_notice_lines(style, ["SESSION TERMINATED", "DATEFORGE OFFLINE"], "red"))
            print(style.red("\n      DateForge launcher closed."))
            time.sleep(1)
            return 0

        print(style.red("      >>> UNKNOWN COMMAND. Choose 1, 2, 3, 4, 5, or 6."))
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
