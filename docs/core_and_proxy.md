# Core Engine and Network Proxy Documentation

This section covers the core logic of the honeypot, located in `src/cyanide/core` and `src/cyanide/proxy`.

## src/cyanide/core

The `src/cyanide/core` directory contains the orchestration logic for the honeypot.

### `server.py`
**Class:** `HoneypotServer`
The main event loop and service orchestrator.
*   **Functions:**
    *   `start()`: Initializes SSH, Telnet, and Metrics servers. Handles `backend_mode` selection (emulated/proxy/pool).
    *   `handle_telnet(reader, writer)`: Handles incoming Telnet connections.
    *   `_analyze_command(cmd, ...)`: Passes commands to the ML filter for anomaly detection.
    *   `save_quarantine_file(...)`: Saves downloaded malware to the quarantine directory.

### `fake_filesystem.py` (and `filesystem_nodes.py`)
**Class:** `FakeFilesystem`
Simulates a Linux filesystem structure in memory (loaded from YAML).
*   **Functions:**
    *   `mkfile(path, content, ...)`: Creates a fake file.
    *   `mkdir_p(path, ...)`: Creates a fake directory recursively.
    *   `remove(path)`: Deletes a file or directory.
    *   `get_content(path)`: Retrieves content of a file, triggering audit callbacks.

### `shell_emulator.py`
**Class:** `ShellEmulator`
Parses and executes command lines input by the attacker. Supports pipes (`|`), redirections (`>`, `>>`), and command chaining (`&&`, `||`, `;`).

---

## src/cyanide/proxy

The `src/cyanide/proxy` directory functionality for relaying traffic to real servers or other honey-tokens.

### `ssh_proxy.py`
**Class:** `HoneypotSSHServer` (Man-in-the-Middle)
*   Intercepts SSH connections.
*   Logs credentials and commands.
*   Forwards traffic to a backend server.

### `tcp_proxy.py`
**Class:** `TCPProxy`
Generic TCP forwarder (used for SMTP, Pure SSH/Telnet proxying).
