# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
"""Command line interface for DateForge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .console import Style, clear_screen
from .history import HistoryError, load_history, record_apply, undo_last_change
from .presets import delete_preset, get_preset, load_presets, save_preset
from .timestamp import (
    TimestampUpdate,
    collect_targets,
    format_local_timestamp,
    normalize_path,
    parse_user_datetime,
    set_path_times,
)

BANNER_LINES = (
    "            ____        _       _____                    ",
    "           |  _ \\  __ _| |_ ___|  ___|__  _ __ __ _  ___ ",
    "           | | | |/ _` | __/ _ \\ |_ / _ \\| '__/ _` |/ _ \\",
    "           | |_| | (_| | ||  __/  _| (_) | | | (_| |  __/",
    "           |____/ \\__,_|\\__\\___|_|  \\___/|_|  \\__, |\\___|",
    "                                              |___/       ",
)
BANNER = "\n".join(BANNER_LINES)
CREDITS_BANNER = "\n".join(
    [
        "        Built by Kieranmcm07",
        "        GitHub: https://github.com/Kieranmcm07",
        "        Forge timestamps cleanly. Leave file contents untouched.",
    ]
)

_THEME_CODES = {
    "green": "92",
    "cyan": "36",
    "blue": "94",
    "magenta": "95",
    "yellow": "93",
    "red": "91",
    "white": "97",
}


def _theme_code(colour: str) -> str:
    return _THEME_CODES.get(colour, _THEME_CODES["green"])


def render_status_rows(style: Style, rows: list[tuple[str, str]], colour: str = "green") -> str:
    code = _theme_code(colour)
    rendered: list[str] = []
    for label, message in rows:
        tag = style.wrap(f"[ {label:<11} ]", code)
        rendered.append(f"      {tag}  {style.wrap(message, code)}")
    return "\n".join(rendered)


def render_notice_lines(style: Style, messages: list[str], colour: str = "green") -> str:
    code = _theme_code(colour)
    return "\n".join(f"      {style.wrap('>>> ' + message, code)}" for message in messages)


def render_terminal_prompt(style: Style, label: str = "dateforge") -> str:
    return style.cyan(f"{label}@local > ")


def default_banner_rows(context: str | None) -> list[tuple[str, str]]:
    if context == "launcher":
        return [
            ("SYSTEM BOOT", "DateForge timestamp console initialized..."),
            ("ACCESS NODE", "Awaiting operator command..."),
            ("TIME CORE", "Filesystem metadata tools online..."),
            ("CREDITS", "Made by Kieranmcm07"),
            ("GITHUB", "https://github.com/Kieranmcm07"),
        ]
    if context == "help":
        return [
            ("HELP NODE", "Timestamp command reference loaded..."),
            ("FORMAT", "YYYY-MM-DD HH:MM:SS, today 18:30, or now"),
            ("TARGETS", "Use --recursive to include folder contents"),
            ("GITHUB", "https://github.com/Kieranmcm07"),
        ]
    if context == "complete":
        return [
            ("ACCESS", "Timestamp write confirmed"),
            ("TIME CORE", "Filesystem metadata updated"),
        ]
    if context == "closed":
        return [
            ("SESSION", "DateForge console terminated"),
            ("STATUS", "Window safe to close"),
        ]
    if context == "interactive":
        return [
            ("SYSTEM BOOT", "Initializing timestamp core..."),
            ("ACCESS NODE", "Waiting for target path and time input..."),
            ("TIME CORE", "Local timezone lock acquired..."),
        ]
    return [
        ("SYSTEM BOOT", "Timestamp core initialized"),
        ("ACCESS NODE", "Scanning target path..."),
        ("TIME CORE", "Using this computer's timezone..."),
    ]


def render_banner(
    style: Style,
    context: str | None = None,
    colour: str = "green",
    rows: list[tuple[str, str]] | None = None,
) -> str:
    code = _theme_code(colour)
    lines = ["", *[f"  {style.wrap(line, code)}" for line in BANNER_LINES], ""]
    lines.append(render_status_rows(style, rows or default_banner_rows(context), colour))
    return "\n".join(lines)


def render_credits(style: Style) -> str:
    return "\n".join(
        [
            f"      {style.magenta('Built by Kieranmcm07')}",
            f"      {style.magenta('GitHub: https://github.com/Kieranmcm07')}",
            f"      {style.magenta('Forge timestamps cleanly. Leave file contents untouched.')}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dateforge",
        description="Change file and folder timestamp metadata.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="File or folder to update. If omitted, interactive mode starts.",
    )
    parser.add_argument(
        "-t",
        "--time",
        dest="time_value",
        help='Desired modified time, preset name, or shortcut like "today 18:30".',
    )
    parser.add_argument(
        "--created",
        dest="created_value",
        help='Desired Windows created time, preset name, or "same" to match --time.',
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="When PATH is a folder, update all child files and folders too.",
    )
    parser.add_argument(
        "--batch",
        metavar="FILE",
        help="Read target paths from a text file, one path per line.",
    )
    parser.add_argument(
        "--include",
        action="append",
        metavar="GLOB",
        help='Only update targets matching this glob, for example "*.txt". Can be repeated.',
    )
    parser.add_argument(
        "--exclude",
        action="append",
        metavar="GLOB",
        help='Skip targets matching this glob, for example "*.bak". Can be repeated.',
    )
    parser.add_argument(
        "--preset",
        dest="preset_name",
        metavar="NAME",
        help="Use a saved preset as the modified time.",
    )
    parser.add_argument(
        "--save-preset",
        nargs=2,
        metavar=("NAME", "TIME"),
        help="Save a reusable timestamp preset.",
    )
    parser.add_argument(
        "--delete-preset",
        metavar="NAME",
        help="Delete a saved timestamp preset.",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List saved timestamp presets.",
    )
    parser.add_argument(
        "--history",
        nargs="?",
        const=10,
        type=int,
        metavar="N",
        help="Show recent DateForge history entries. Defaults to 10.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Restore the most recent unapplied DateForge change from history.",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Hide the ASCII banner.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print errors and the final count.",
    )
    return parser


def read_prompt(message: str) -> str:
    try:
        return input(message)
    except EOFError as exc:
        raise ValueError("Path and time are required when running non-interactively.") from exc


def ask_yes_no(message: str, default: bool = False) -> bool:
    style = Style()
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = read_prompt(style.cyan(f"{message} {suffix}: ")).strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print(style.yellow("      Please answer yes or no."))


def _management_command_count(args: argparse.Namespace) -> int:
    return sum(
        bool(command)
        for command in (
            args.undo,
            args.history is not None,
            args.list_presets,
            args.save_preset,
            args.delete_preset,
        )
    )


def _is_management_command(args: argparse.Namespace) -> bool:
    return _management_command_count(args) > 0


def prompt_for_missing_values(args: argparse.Namespace) -> None:
    style = Style()
    prompted = False

    if not args.path and not args.batch:
        prompted = True
        args.path = read_prompt(render_terminal_prompt(style, "target.path")).strip().strip('"')

    if not args.time_value and not args.created_value and not args.preset_name:
        prompted = True
        print(style.dim("      Examples: 2026-05-15 18:30:00 | today 18:30 | tomorrow 09:00 | now"))
        args.time_value = read_prompt(render_terminal_prompt(style, "target.time")).strip()

    if not args.path and not args.batch:
        raise ValueError("A file or folder path is required.")

    if not args.time_value and not args.created_value and not args.preset_name:
        raise ValueError("A desired modified or created time is required.")

    target = normalize_path(args.path) if args.path else None
    if prompted and target is not None and target.is_dir() and not args.recursive:
        args.recursive = ask_yes_no("Update everything inside this folder too?")


def read_batch_paths(batch_file: str) -> list[Path]:
    batch_path = normalize_path(batch_file)
    if not batch_path.exists():
        raise FileNotFoundError(f"Batch file does not exist: {batch_path}")
    if not batch_path.is_file():
        raise ValueError(f"Batch path is not a file: {batch_path}")

    batch_root = batch_path.resolve().parent
    paths: list[Path] = []
    for line_number, line in enumerate(batch_path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip().lstrip("\ufeff")
        if not text or text.startswith("#"):
            continue
        try:
            target = normalize_path(text)
        except ValueError as exc:
            raise ValueError(f"Invalid batch path on line {line_number}: {exc}") from exc
        if not target.is_absolute():
            target = batch_root / target
        paths.append(target)

    if not paths:
        raise ValueError("Batch file does not contain any target paths.")
    return paths


def collect_requested_targets(args: argparse.Namespace) -> list[Path]:
    roots: list[Path | str] = []
    if args.path:
        roots.append(args.path)
    if args.batch:
        roots.extend(read_batch_paths(args.batch))

    targets: list[Path] = []
    for root in roots:
        targets.extend(
            collect_targets(
                root,
                recursive=args.recursive,
                include=args.include,
                exclude=args.exclude,
            )
        )

    seen: set[Path] = set()
    unique_targets: list[Path] = []
    for target in targets:
        key = target.resolve()
        if key in seen:
            continue
        seen.add(key)
        unique_targets.append(target)

    if not unique_targets:
        raise ValueError("No targets matched the requested path and filter settings.")
    return unique_targets


def resolve_timestamp_value(value: str) -> float:
    try:
        return parse_user_datetime(value)
    except ValueError as parse_error:
        try:
            return get_preset(value)
        except KeyError as preset_error:
            raise parse_error from preset_error


def resolve_requested_timestamps(args: argparse.Namespace) -> tuple[float | None, float | None]:
    if args.time_value and args.preset_name:
        raise ValueError("Use either --time or --preset, not both.")

    modified_timestamp = None
    if args.preset_name:
        try:
            modified_timestamp = get_preset(args.preset_name)
        except KeyError as exc:
            raise ValueError(f"Preset not found: {args.preset_name}") from exc
    elif args.time_value:
        modified_timestamp = resolve_timestamp_value(args.time_value)

    created_timestamp = None
    if args.created_value:
        if args.created_value.strip().lower() == "same":
            if modified_timestamp is None:
                raise ValueError('--created "same" requires --time or --preset.')
            created_timestamp = modified_timestamp
        else:
            created_timestamp = resolve_timestamp_value(args.created_value)

    if modified_timestamp is None and created_timestamp is None:
        raise ValueError("A desired modified or created time is required.")

    return modified_timestamp, created_timestamp


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _format_optional_timestamp(timestamp: float | None) -> str:
    if timestamp is None:
        return "not available"
    return format_local_timestamp(timestamp)


def print_update(update: TimestampUpdate, style: Style, label: str = "APPLY", colour: str = "green") -> None:
    status = style.wrap(f"[ {label:<11} ]", _theme_code(colour))
    print(f"      {status}  {display_path(update.path)}")
    if update.modified_requested:
        before = format_local_timestamp(update.before_modified)
        after = format_local_timestamp(update.after_modified)
        print(f"                    modified  {style.dim(before)} -> {style.white(after)}")
    if update.created_requested:
        before = _format_optional_timestamp(update.before_created)
        after = _format_optional_timestamp(update.after_created)
        print(f"                    created   {style.dim(before)} -> {style.white(after)}")


def print_presets(style: Style) -> int:
    try:
        presets = load_presets()
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    if not presets:
        print(style.yellow("      No presets saved yet."))
        return 0

    print(render_notice_lines(style, ["SAVED PRESETS"], "magenta"))
    print()
    for name, timestamp in sorted(presets.items()):
        print(f"      {style.magenta(name)}  {format_local_timestamp(timestamp)}")
    return 0


def save_requested_preset(args: argparse.Namespace, style: Style) -> int:
    name, time_value = args.save_preset
    try:
        timestamp = parse_user_datetime(time_value)
        normalized = save_preset(name, timestamp)
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    print(f"      {style.green('>>> PRESET SAVED')} {normalized} = {format_local_timestamp(timestamp)}")
    return 0


def delete_requested_preset(args: argparse.Namespace, style: Style) -> int:
    try:
        normalized = delete_preset(args.delete_preset)
    except KeyError:
        print(f"{style.red('Error:')} Preset not found: {args.delete_preset}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    print(f"      {style.green('>>> PRESET DELETED')} {normalized}")
    return 0


def print_history(style: Style, limit: int) -> int:
    if limit < 1:
        print(f"{style.red('Error:')} History limit must be at least 1.", file=sys.stderr)
        return 1

    try:
        entries = load_history()
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    if not entries:
        print(style.yellow("      No DateForge history has been recorded yet."))
        return 0

    print(render_notice_lines(style, [f"RECENT HISTORY ({min(limit, len(entries))})"], "blue"))
    print()
    for entry in reversed(entries[-limit:]):
        action = str(entry.get("action", "unknown")).upper()
        entry_id = str(entry.get("id", ""))[:8]
        run_at = format_local_timestamp(float(entry.get("run_at", 0)))
        count = len(entry.get("changes", []))
        extra = ""
        if entry.get("action") == "undo" and entry.get("undo_of"):
            extra = f" undo of {str(entry['undo_of'])[:8]}"
        print(f"      {style.blue(action):<16} {entry_id}  {run_at}  {count} item(s){extra}")
    return 0


def run_undo(style: Style, quiet: bool) -> int:
    try:
        result = undo_last_change()
    except HistoryError as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    if not quiet:
        print(render_notice_lines(style, ["UNDO RESTORE COMPLETE"], "cyan"))
        print()
        for update in result.updates:
            print_update(update, style, "UNDO", "cyan")

    for failure in result.failures:
        print(f"{style.red('[FAIL]')} {display_path(failure.path)} - {failure.error}", file=sys.stderr)

    if result.failures:
        print(
            f"\n      {style.yellow('>>> UNDO COMPLETE WITH WARNINGS')} "
            f"{len(result.updates)} restored, {len(result.failures)} failed."
        )
        return 2

    print(f"\n      {style.green('>>> UNDO COMPLETE')} {len(result.updates)} item(s) restored.")
    return 0


def run_management_command(args: argparse.Namespace, style: Style) -> int | None:
    if _management_command_count(args) > 1:
        print(f"{style.red('Error:')} Choose one management command at a time.", file=sys.stderr)
        return 1

    if args.save_preset:
        return save_requested_preset(args, style)
    if args.delete_preset:
        return delete_requested_preset(args, style)
    if args.list_presets:
        return print_presets(style)
    if args.history is not None:
        return print_history(style, args.history)
    if args.undo:
        return run_undo(style, args.quiet)
    return None


def run(args: argparse.Namespace) -> int:
    style = Style(enabled=None if not args.quiet else False)
    management_result = run_management_command(args, style)
    if management_result is not None:
        return management_result

    interactive_mode = not _is_management_command(args) and (
        (not args.path and not args.batch)
        or (not args.time_value and not args.created_value and not args.preset_name)
    )

    if not args.quiet and not args.no_banner:
        if interactive_mode:
            clear_screen()
        banner_context = "interactive" if interactive_mode else "cli"
        banner_colour = "cyan"
        print(render_banner(style, banner_context, banner_colour))
        start_message = (
            "      >>> DATEFORGE TERMINAL READY"
            if interactive_mode
            else "      >>> TARGET SCAN INITIALIZED"
        )
        print(style.wrap(f"\n{start_message}\n", _theme_code(banner_colour)))

    try:
        prompt_for_missing_values(args)
        modified_timestamp, created_timestamp = resolve_requested_timestamps(args)
        targets = collect_requested_targets(args)
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        status_rows: list[tuple[str, str]] = []
        if modified_timestamp is not None:
            status_rows.append(("MODIFIED", format_local_timestamp(modified_timestamp)))
        if created_timestamp is not None:
            status_rows.append(("CREATED", format_local_timestamp(created_timestamp)))
        status_rows.extend(
            [
                ("MODE", "apply changes"),
                ("ITEMS", str(len(targets))),
            ]
        )
        if args.include:
            status_rows.append(("INCLUDE", ", ".join(args.include)))
        if args.exclude:
            status_rows.append(("EXCLUDE", ", ".join(args.exclude)))

        print(render_notice_lines(style, ["TARGET SCAN COMPLETE", "TIMESTAMP WRITE ARMED"], "green"))
        print()
        print(render_status_rows(style, status_rows, "green"))
        print()

    updates: list[TimestampUpdate] = []
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
            print(f"{style.red('[FAIL]')} {display_path(target)} - {exc}", file=sys.stderr)
            continue

        updates.append(update)
        if not args.quiet:
            print_update(update, style)

    history_saved = None
    if updates:
        try:
            history_saved = record_apply(updates)
        except OSError as exc:
            print(f"{style.yellow('Warning:')} Could not write history log: {exc}", file=sys.stderr)

    if failed:
        print(
            f"\n      {style.yellow('>>> DATEFORGE COMPLETE WITH WARNINGS')} "
            f"{len(updates)} updated, {failed} failed."
        )
        return 2

    print(f"\n      {style.green('>>> DATEFORGE COMPLETE')} {len(updates)} item(s) updated.")
    if history_saved and not args.quiet:
        print(f"      {style.dim('History ID:')} {str(history_saved.get('id', ''))[:8]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)
