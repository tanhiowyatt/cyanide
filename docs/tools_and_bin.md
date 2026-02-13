# Tools and Scripts

## scripts/

Executable scripts exposed to the user.

*   **`cyanide`**: The main entry point. Supports the following commands:
    *   `start`, `stop`, `restart`: Manage the honeypot process.
    *   `stats`: Display real-time statistics.
    *   `clean`: Remove old logs (supports `--days`, `--dry-run`, `--all`).
    *   `replay <file>`: Convert TTY logs to asciinema format.

## Root Scripts

Helper scripts for development and analysis.

*   **`generate_mass_fs.py`**: Creates a massive `fs.yaml` for testing.
*   **`generate_profiles.py`**: Generates OS-specific YAML templates in `config/fs-config/`.

---

# User Instructions

## How to Replay an Attacker Session

When an attacker interacts with the honeypot (via SSH or Telnet), their complete TTY session is logged. You can watch exactly what they saw and typed.

1.  **Locate the session log:**
    Check `var/log/cyanide/tty/` in your local project folder (mounted volume).
    ```bash
    ls -l var/log/cyanide/tty/
    ```

2.  **Play the session:**
    Run the replay command from the root of the project:
    
    ```bash
    ./scripts/cyanide replay var/log/cyanide/tty/ssh_X.X.X.X_sessionID/session.log > playback.cast
    ```

## How to Modify the Fake Filesystem

Edit the YAML template for the desired profile in `config/fs-config/` (e.g., `fs.ubuntu_22_04.yaml`) directly:

```bash
# On host machine:
nano config/fs-config/fs.ubuntu_22_04.yaml

# Add a honey file:
# - name: confidential.txt
#   type: file
#   perm: "-rw-------"
#   content: |
#     API_KEY=sk-1...

# Restart container:
docker compose -f docker/docker-compose.yml restart cyanide
```

**That's it!** Changes will take effect immediately for new sessions.

