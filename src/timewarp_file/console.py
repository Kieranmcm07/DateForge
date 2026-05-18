# ============================================================
#   Made by Kieranmcm07 on GitHub
#   GitHub: https://github.com/Kieranmcm07
# ============================================================
"""Console helpers for the TimeWarp File command line tools."""

from __future__ import annotations

import ctypes
import os
import sys


def enable_ansi() -> bool:
    """Enable ANSI colours on Windows when the terminal supports them."""
    if os.environ.get("NO_COLOR"):
        return False

    if os.name != "nt":
        return True

    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False

        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError):
        return False


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


class Style:
    """Small ANSI styling helper with a safe no-colour fallback."""

    def __init__(self, enabled: bool | None = None) -> None:
        self.enabled = sys.stdout.isatty() and enable_ansi() if enabled is None else enabled

    def wrap(self, text: str, code: str) -> str:
        if not self.enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def bold(self, text: str) -> str:
        return self.wrap(text, "1")

    def cyan(self, text: str) -> str:
        return self.wrap(text, "36")

    def teal(self, text: str) -> str:
        return self.wrap(text, "38;5;45")

    def blue(self, text: str) -> str:
        return self.wrap(text, "94")

    def green(self, text: str) -> str:
        return self.wrap(text, "92")

    def magenta(self, text: str) -> str:
        return self.wrap(text, "95")

    def violet(self, text: str) -> str:
        return self.wrap(text, "38;5;141")

    def pink(self, text: str) -> str:
        return self.wrap(text, "38;5;205")

    def yellow(self, text: str) -> str:
        return self.wrap(text, "93")

    def red(self, text: str) -> str:
        return self.wrap(text, "91")

    def white(self, text: str) -> str:
        return self.wrap(text, "97")

    def grey(self, text: str) -> str:
        return self.wrap(text, "90")

    def dim(self, text: str) -> str:
        return self.wrap(text, "2")
