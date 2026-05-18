# DateForge

```
            ____        _       _____
           |  _ \  __ _| |_ ___|  ___|__  _ __ __ _  ___
           | | | |/ _` | __/ _ \ |_ / _ \| '__/ _` |/ _ \
           | |_| | (_| | ||  __/  _| (_) | | | (_| |  __/
           |____/ \__,_|\__\___|_|  \___/|_|  \__, |\___|
                                              |___/
```

DateForge is a clean Python CLI for changing the **date modified** timestamp of a file or folder to a time you choose.

It is designed to be simple enough for everyday use and tidy enough to publish as a GitHub project.

## Start Here

On Windows, double-click:

```text
run.bat
```

That opens the full launcher menu with the styled banner.

You can also run it from PowerShell:

```powershell
py launcher.py
```

## Features

- Change a single file or folder modified timestamp.
- Recursively update everything inside a folder.
- Styled launcher menu with a Windows batch runner.
- Interactive mode when you run the launcher or CLI without arguments.
- Optional CLI preview mode for checking folder changes first.
- No third-party dependencies.
- Works with local system time by default.

## Quick Start

Run directly:

```powershell
py launcher.py
```

Or pass everything in one command:

```powershell
py dateforge.py "C:\path\to\file.txt" --time "2026-05-15 18:30:00"
```

Update a folder itself:

```powershell
py dateforge.py "C:\path\to\folder" --time "2026-05-15 18:30:00"
```

Update every item inside a folder too:

```powershell
py dateforge.py "C:\path\to\folder" --time "2026-05-15 18:30:00" --recursive
```

Optional: preview changes without touching anything:

```powershell
py dateforge.py "C:\path\to\file.txt" --time "2026-05-15 18:30:00" --dry-run
```

If `python` is available on your PATH, you can use `python` instead of `py`.

## Accepted Time Formats

Recommended:

```text
YYYY-MM-DD HH:MM
YYYY-MM-DD HH:MM:SS
YYYY-MM-DDTHH:MM:SS
YYYY/MM/DD HH:MM
YYYY/MM/DD HH:MM:SS
```

Also supported:

```text
MM/DD/YYYY HH:MM
MM/DD/YYYY HH:MM:SS
now
```

Examples:

```text
2026-05-15 18:30
2026-05-15 18:30:45
2026/05/15 18:30
05/15/2026 18:30
now
```

## Install As A CLI

From the project root:

```powershell
py -m pip install -e .
```

Then run:

```powershell
dateforge "C:\path\to\file.txt" --time "2026-05-15 18:30:00"
```

The older `timewarp` and `timewarp-file` commands are also kept as aliases.

## Notes

- This changes the modified timestamp metadata only. It does not edit file contents.
- By default, access time is preserved while modified time is changed.
- On folders, `--recursive` updates child files and folders before resetting the root folder timestamp.
- Some protected files may require elevated permissions.

## Development

Run the test suite:

```powershell
py -m pip install -e .
py -m unittest discover
```

Show the CLI help:

```powershell
py dateforge.py --help
```
