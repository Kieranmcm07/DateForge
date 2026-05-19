<!--
  ============================================================
    Made by Kieranmcm07 on GitHub
    GitHub: https://github.com/Kieranmcm07
  ============================================================
-->

<h1 align="center">DateForge</h1>

<p align="center">
  A polished Python timestamp toolkit for changing the <strong>date modified</strong>
  value of files and folders from a clean hacker-terminal styled launcher.
  <br>
  Single files, folders, recursive folder updates, undo history, batch updates,
  saved presets, filters, Windows created-time support, and friendly time
  shortcuts all run from one lightweight console tool.
</p>

<p align="center">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <a href="LICENSE">
    <img alt="MIT license" src="https://img.shields.io/badge/License-MIT-2ea043?style=for-the-badge">
  </a>
  <img alt="No dependencies" src="https://img.shields.io/badge/Dependencies-none-00A86B?style=for-the-badge">
  <img alt="Windows launcher" src="https://img.shields.io/badge/Windows-launcher-0078D4?style=for-the-badge&logo=windows&logoColor=white">
</p>

<p align="center">
  <a href="#timestamp-workflow">Workflow</a>
  |
  <a href="#features">Features</a>
  |
  <a href="#setup">Setup</a>
  |
  <a href="#command-overview">Commands</a>
  |
  <a href="#accepted-time-formats">Time Formats</a>
  |
  <a href="#development">Development</a>
</p>

```text
            ____        _       _____
           |  _ \  __ _| |_ ___|  ___|__  _ __ __ _  ___
           | | | |/ _` | __/ _ \ |_ / _ \| '__/ _` |/ _ \
           | |_| | (_| | ||  __/  _| (_) | | | (_| |  __/
           |____/ \__,_|\__\___|_|  \___/|_|  \__, |\___|
                                              |___/
```

<p align="center">
  <strong>Built for quick local file work:</strong>
  pick a target, choose the modified time you want, and let DateForge update
  metadata without editing file contents. Every successful update is logged so
  the last DateForge change can be restored.
</p>

## Timestamp Workflow

<table>
  <tr>
    <td width="33%" align="center">
      <strong>1. Choose A Target</strong><br>
      Paste, type, or drag a file/folder path into the launcher or CLI.
    </td>
    <td width="33%" align="center">
      <strong>2. Set The Time</strong><br>
      Use a full timestamp like <code>2026-05-15 18:30:00</code>, or a shortcut
      like <code>today 18:30</code>, <code>tomorrow 09:00</code>, or <code>now</code>.
    </td>
    <td width="33%" align="center">
      <strong>3. Forge Metadata</strong><br>
      Apply modified and optional created timestamps while DateForge shows each
      processed target and records an undoable history entry.
    </td>
  </tr>
</table>

## At A Glance

<table>
  <tr>
    <td width="25%" align="center">
      <strong>Terminal Launcher</strong><br>
      Green-on-black console style, ASCII banner, boot rows, and command prompts.
    </td>
    <td width="25%" align="center">
      <strong>Timestamp Engine</strong><br>
      Updates modified-time metadata while preserving access time by default.
    </td>
    <td width="25%" align="center">
      <strong>Folder Control</strong><br>
      Update a folder itself, recursively process children, or filter by glob.
    </td>
    <td width="25%" align="center">
      <strong>Undo History</strong><br>
      Restore the most recent DateForge change or inspect the history log.
    </td>
  </tr>
</table>

## Features

<table>
  <tr>
    <td width="50%">
      <strong>Styled launcher menu</strong><br>
      Open <code>run.bat</code> on Windows for the full DateForge console with neon status
      rows, access messages, and a simple numbered menu.
    </td>
    <td width="50%">
      <strong>Direct CLI commands</strong><br>
      Run <code>dateforge.py</code>, the installed <code>dateforge</code> command, or the
      legacy <code>timewarp</code> aliases when you want one-shot terminal usage.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>Single target updates</strong><br>
      Change the modified timestamp for one file or one folder without editing its contents.
    </td>
    <td width="50%">
      <strong>Recursive folder updates</strong><br>
      Process everything inside a folder, then reset the root folder timestamp last.
      Include and exclude glob filters can limit which targets are touched.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>Human-friendly time input</strong><br>
      Accepts exact date/time values plus shortcuts like <code>now</code>, <code>noon</code>,
      <code>midnight</code>, <code>today 18:30</code>, and <code>6:30pm</code>.
    </td>
    <td width="50%">
      <strong>No third-party dependencies</strong><br>
      Uses the Python standard library only, so setup stays small and local.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>Undo and history log</strong><br>
      Every successful update is written to a local JSONL history file. Run
      <code>--undo</code> to restore the latest unapplied DateForge change.
    </td>
    <td width="50%">
      <strong>Batch files and presets</strong><br>
      Update many paths from a text file, save named timestamp presets, and reuse
      those presets from either modified-time or created-time commands.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>Windows created time</strong><br>
      On Windows, DateForge can update file/folder created time with
      <code>--created</code> while still supporting modified-time changes.
    </td>
    <td width="50%">
      <strong>Local-only storage</strong><br>
      Presets and history are stored on your machine under the DateForge app data
      folder by default.
    </td>
  </tr>
</table>

## Setup

1. Clone or download the project.

```bash
git clone https://github.com/Kieranmcm07/DateForge.git
cd DateForge
```

2. Start the Windows launcher.

```text
run.bat
```

3. Or run it from PowerShell.

```powershell
py launcher.py
```

If the Python launcher is not available on your machine, use your normal Python
command instead:

```powershell
python launcher.py
```

## Windows Helper Script

The repository includes one Windows batch file for quick local use:

| Script | Purpose |
| --- | --- |
| `run.bat` | Open the styled DateForge launcher menu |

## Command Overview

Run directly from the project root:

```powershell
py dateforge.py "C:\path\to\file.txt" --time "2026-05-15 18:30:00"
```

| Command / Option | Description |
| --- | --- |
| `py launcher.py` | Open the interactive DateForge launcher |
| `py dateforge.py` | Run the CLI from the repository root |
| `dateforge` | Installed console command after `pip install -e .` |
| `timewarp` | Legacy command alias |
| `timewarp-file` | Legacy command alias |
| `PATH` | File or folder to update |
| `--time "YYYY-MM-DD HH:MM:SS"` | Desired modified timestamp |
| `--created "YYYY-MM-DD HH:MM:SS"` | Desired Windows created timestamp |
| `--recursive` | Update child files and folders when the target is a folder |
| `--include "*.txt"` | Only update targets matching a glob pattern |
| `--exclude "*.bak"` | Skip targets matching a glob pattern |
| `--batch targets.txt` | Read target paths from a text file |
| `--preset NAME` | Use a saved preset as the modified timestamp |
| `--save-preset NAME TIME` | Save a reusable timestamp preset |
| `--delete-preset NAME` | Delete a saved preset |
| `--list-presets` | Show saved presets |
| `--history [N]` | Show recent history entries |
| `--undo` | Restore the latest unapplied DateForge change |
| `--no-banner` | Hide the ASCII banner for cleaner command output |
| `--quiet` | Print only errors and the final count |

## Quick Examples

Update one file:

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

Update only text files in a folder tree:

```powershell
py dateforge.py "C:\path\to\folder" --time "2026-05-15 18:30:00" --recursive --include "*.txt"
```

Skip temporary files during a recursive update:

```powershell
py dateforge.py "C:\path\to\folder" --time "2026-05-15 18:30:00" --recursive --exclude "*.tmp"
```

Update Windows created time too:

```powershell
py dateforge.py "C:\path\to\file.txt" --time "2026-05-15 18:30:00" --created same
```

Update targets from a batch file:

```powershell
py dateforge.py --batch targets.txt --time "2026-05-15 18:30:00"
```

Save and use a preset:

```powershell
py dateforge.py --save-preset release "2026-05-15 18:30:00"
py dateforge.py "C:\path\to\file.txt" --preset release
```

Show history or undo the latest DateForge change:

```powershell
py dateforge.py --history
py dateforge.py --undo
```

## Accepted Time Formats

Recommended formats:

```text
YYYY-MM-DD HH:MM
YYYY-MM-DD HH:MM:SS
YYYY-MM-DDTHH:MM:SS
YYYY/MM/DD HH:MM
YYYY/MM/DD HH:MM:SS
today HH:MM
tomorrow HH:MM
yesterday HH:MM
```

Also supported:

```text
MM/DD/YYYY HH:MM
MM/DD/YYYY HH:MM:SS
now
noon
midnight
```

Examples:

```text
2026-05-15 18:30
2026-05-15 18:30:45
2026/05/15 18:30
05/15/2026 18:30
today 18:30
tomorrow 09:00
yesterday
6:30pm
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

## Data And Behaviour Notes

- DateForge changes timestamp metadata only. It does not edit file contents.
- DateForge can also change Windows created time when `--created` is used.
- Access time is preserved while modified time is changed.
- On folders, `--recursive` updates child files and folders before resetting the root folder timestamp.
- `--include` and `--exclude` accept glob patterns and can be repeated.
- Batch files use one target path per line. Blank lines and lines starting with `#` are ignored.
- Successful updates are recorded in a local history log so `--undo` can restore the latest unapplied change.
- Presets and history are stored in the DateForge app data folder by default.
- Some protected files may require elevated permissions.
- DateForge uses your local system timezone by default.

## Project Structure

```text
.
|-- src/
|   `-- timewarp_file/
|       |-- __init__.py
|       |-- __main__.py
|       |-- cli.py
|       |-- console.py
|       |-- history.py
|       |-- presets.py
|       `-- timestamp.py
|-- tests/
|   |-- __init__.py
|   |-- test_features.py
|   `-- test_timestamp.py
|-- dateforge.py
|-- launcher.py
|-- timewarp.py
|-- run.bat
|-- pyproject.toml
|-- LICENSE
`-- README.md
```

## Development

Install the project in editable mode:

```powershell
py -m pip install -e .
```

Run the test suite:

```powershell
py -m unittest discover
```

Show the CLI help:

```powershell
py dateforge.py --help
```

## License

This project is licensed under the MIT License.
