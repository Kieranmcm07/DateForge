"""Command line interface for TimeWarp File."""

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

BANNER = r"""
    _______ _                 __        __                 
   |__   __(_)                \ \      / /                 
      | |   _ _ __ ___   ___   \ \ /\ / /_ _ _ __ _ __    
      | |  | | '_ ` _ \ / _ \   \ V  V / _` | '__| '_ \   
      | |  | | | | | | |  __/    \_/\_/ (_| | |  | |_) |  
      |_|  |_|_| |_| |_|\___|             \__,_|_|  | .__/ 
                                                     | |    
                                                     |_|    

        [ TIME CORE  ]  File and folder timestamp control
        [ SAFE MODE  ]  Dry-run preview available before changes
        [ LOCAL TIME ]  Uses your computer's local timezone
"""

CREDITS_BANNER = r"""
        Built by Kieranmcm07
        GitHub: https://github.com/Kieranmcm07
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="timewarp-file",
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
    label = "DRY" if dry_run else "OK"
    status = style.yellow(label) if dry_run else style.green(label)
    before = format_local_timestamp(update.before_modified)
    after = format_local_timestamp(update.after_modified)
    print(f"[{status}] {display_path(update.path)}")
    print(f"     {style.dim(before)} -> {after}")


def run(args: argparse.Namespace) -> int:
    style = Style(enabled=None if not args.quiet else False)
    interactive_mode = not args.path or not args.time_value

    if not args.quiet and not args.no_banner:
        if interactive_mode:
            clear_screen()
        print(style.cyan(BANNER))
        print(style.magenta(CREDITS_BANNER))
        print(style.cyan("Starting TimeWarp File. Follow the prompts below.\n"))

    try:
        prompt_for_missing_values(args)
        desired_timestamp = parse_user_datetime(args.time_value)
        targets = collect_targets(args.path, recursive=args.recursive)
    except (OSError, ValueError) as exc:
        print(f"{style.red('Error:')} {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Target time: {format_local_timestamp(desired_timestamp)}")
        print(f"Mode: {'dry run' if args.dry_run else 'apply'}")
        print(f"Items: {len(targets)}\n")

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
        print(f"\n{style.yellow('Done with warnings:')} {changed} {verb}, {failed} failed.")
        return 2

    print(f"\n{style.green('Done:')} {changed} item(s) {verb}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)
