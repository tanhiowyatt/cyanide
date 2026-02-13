# Filesystem and Commands Documentation

## src/cyanide/fs

Utilities for managing the persistence of the Fake Filesystem.

### `yaml_fs.py`
Methods for loading the filesystem state from YAML.
*   `load_fs(path)`: Loads and parses the filesystem tree and OS metadata from a YAML file. Returns `(root_node, metadata_dict)`.

### Filesystem Metadata
Each YAML template in `config/fs-config/` supports a `metadata:` section at the top. This metadata is used by the `HoneypotServer` to configure session-specific attributes:
- `os_name`: Descriptive name of the OS.
- `ssh_banner`: Version string for the SSH listener.
- `uname_r`: Kernel release version.
- `uname_a`: Full uname output.
- `proc_version`: Content for `/proc/version`.

---

## src/commands

This directory contains the implementations of individual shell commands. Each file typically corresponds to one or more commands.

### `base.py`
**Class:** `Command/Executable`
Base class for all commands.
*   `execute(args, input_data)`: Must be implemented by subclasses. `input_data` contains stdin (from pipes).

### `file_ops.py`
Handles file manipulation.
*   **Classes:**
    *   `TouchCommand`: Updates timestamps or creates empty files.
    *   `MkdirCommand`: Creates directories (supports `-p`).
    *   `RmCommand`: Removes files (supports `-rf`).
    *   `RmdirCommand`: Removes empty directories.
    *   `CpCommand`: Copies files.
    *   `MvCommand`: Moves/Renames files.

### `ls.py` (`LsCommand`)
List directory contents. Supports flags like `-l`, `-a`, `-la`. Formats output to look like real Linux `ls`.

### `cd.py` (`CdCommand`)
Changes the current working directory of the `ShellEmulator`. Handles `..`, `.`, `~`, and `-`.

### `cat.py` (`CatCommand`)
Outputs file content to stdout.

### `net_ops.py` / `misc.py`
*   `WgetCommand` / `CurlCommand`: Simulates downloading files. *Critical for malware collection.* Saves files to the filesystem and triggers quarantine.

### Adding a New Command
1. Create a new file in `src/commands/` (e.g., `mycmd.py`).
2. Inherit from `Command`.
3. Implement `async def execute(self, args, input_data)`.
4. Register the command in `src/commands/__init__.py` inside `COMMAND_MAP`.
