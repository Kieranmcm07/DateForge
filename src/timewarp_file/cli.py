"""Command line interface for DateForge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .console import Style, clear_screen
from .timestamp import (
    TimestampUpdate,
    collect_targets,
    format_local_timestamp,
    normalize_path,
    parse_user_datetime,
    set_modified_time,
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
CREDITS_BANNER = "Built by Kieranmcm07 | GitHub: https://github.com/Kieranmcm07"

_THEME_CODES = {
    "green": "92",
    "cyan": "96",
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


def default_banner_rows(context: str | None) -> list[tuple[str, str]]:
    if context == "launcher":
        return [
            ("ACCESS", "Timestamp console online"),
            ("TIME CORE", "Modified-date editor ready"),
            ("CREDITS", "Made by Kieranmcm07"),
            ("GITHUB", "https://github.com/Kieranmcm07"),
        ]
    if context == "help":
        return [
            ("HELP", "Showing timestamp command notes"),
            ("FORMAT", "Use YYYY-MM-DD HH:MM:SS or now"),
            ("GITHUB", "https://github.com/Kieranmcm07"),
        ]
    if context == "complete":
        return [
            ("TIMESTAMP", "Modified-date update complete"),
            ("STATUS", "Filesystem metadata written"),
        ]
    if context == "preview":
        return [
            ("PREVIEW", "No file metadata was changed"),
            ("STATUS", "Timestamp plan complete"),
        ]
    if context == "closed":
        return [
            ("SESSION", "DateForge launcher closed"),
            ("STATUS", "Console safe to exit"),
        ]
    if context == "interactive":
        return [
            ("SYSTEM BOOT", "Initializing timestamp core..."),
            ("ACCESS NODE", "Waiting for path and time input..."),
            ("LOCAL TIME", "Using this computer's timezone..."),
        ]
    return [
        ("SYSTEM BOOT", "Timestamp core initialized"),
        ("ACCESS NODE", "Scanning target path..."),
        ("LOCAL TIME", "Using this computer's timezone..."),
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
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dateforge",
        description="Change the date modified timestamp of a file or folder.",
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
        help='Desired modified time, for example "2026-05-15 18:30:00" or "now".',
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="When PATH is a folder, update all child files and folders too.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the planned changes without modifying timestamps.",
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
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = read_prompt(f"{message} {suffix}: ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def prompt_for_missing_values(args: argparse.Namespace) -> None:
    prompted = False

    if not args.path:
        prompted = True
        args.path = read_prompt("File or folder path: ").strip().strip('"')

    if not args.time_value:
        prompted = True
        args.time_value = read_prompt("New modified time: ").strip()

    if not args.path:
        raise ValueError("A file or folder path is required.")

    if not args.time_value:
        raise ValueError("A desired time is required.")

    target = normalize_path(args.path)
    if prompted and target.is_dir() and not args.recursive:
        args.recursive = ask_yes_no("Update everything inside this folder too?")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def print_update(update: TimestampUpdate, style: Style, dry_run: bool) -> None:
    label = "PREVIEW" if dry_run else "APPLY"
    colour = "yellow" if dry_run else "green"
    status = style.wrap(f"[ {label:<11} ]", _theme_code(colour))
    before = format_local_timestamp(update.before_modified)
    after = format_local_timestamp(update.after_modified)
    print(f"      {status}  {display_path(update.path)}")
    print(f"                    {style.dim(before)} -> {style.white(after)}")


def run(args: argparse.Namespace) -> int:
    style = Style(enabled=None if not args.quiet else False)
    interactive_mode = not args.path or not args.time_value

    if not args.quiet and not args.no_banner:
        if interactive_mode:
            clear_screen()
        banner_context = "interactive" if interactive_mode else "cli"
        banner_colour = "yellow" if args.dry_run else "cyan"
        print(render_banner(style, banner_context, banner_colour))
        start_message = (
            "      Starting DateForge. Follow the prompts below."
            if interactive_mode
            else "      DateForge ready. Checking targets..."
        )
        print(style.wrap(f"\n{start_message}\n", _theme_code(banner_colour)))

    try:
        prompt_for_missing_values(args)
        desired_timestamp = parse_user_datetime(args.time_value)
        targets = collect_targets(args.path, recursive=args.recursive)
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        action = "TIMESTAMP PREVIEW READY" if args.dry_run else "TIMESTAMP WRITE ARMED"
        colour = "yellow" if args.dry_run else "green"
        print(render_notice_lines(style, ["TARGET SCAN COMPLETE", action], colour))
        print()
        print(f"      Target time: {format_local_timestamp(desired_timestamp)}")
        print(f"      Mode: {'preview only' if args.dry_run else 'apply changes'}")
        print(f"      Items: {len(targets)}\n")

    changed = 0
    failed = 0

    for target in targets:
        try:
            update = set_modified_time(target, desired_timestamp, dry_run=args.dry_run)
        except OSError as exc:
            failed += 1
            print(f"{style.red('[FAIL]')} {display_path(target)} - {exc}", file=sys.stderr)
            continue

        changed += 1
        if not args.quiet:
            print_update(update, style, args.dry_run)

    verb = "would be updated" if args.dry_run else "updated"
    if failed:
        print(f"\n      {style.yellow('Done with warnings:')} {changed} {verb}, {failed} failed.")
        return 2

    print(f"\n      {style.green('Done:')} {changed} item(s) {verb}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)
