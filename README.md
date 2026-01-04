# Advanced SSH/Telnet Honeypot

A high-interaction SSH and Telnet honeypot written in Python, designed to mimic a realistic Linux server and capture attacker activity. It features strict JSON logging, a real-time web dashboard, and Docker support.

## Features

- **Dual Protocol Support**: run SSH (default port 2222) and Telnet (default port 2223) servers simultaneously.
- **Realistic Emulation**:
  - **Fake Filesystem**: In-memory filesystem with realistically populated directories (`/etc`, `/home`, `/var`).
  - **Command Emulation**: Supports common commands like `ls`, `cd`, `cat`, `pwd`, `whoami`, `id`, `uname`, `ps`, and `sudo`.
  - **Dynamic Responses**: `sudo` prompts for passwords, `cat` works on fake files.
- **Advanced Logging**:
  - Activity is logged to `logs/honeypot-YYYY-MM-DD.jsonl`.
  - Captures source IP, credentials, all executed commands, and session duration.
  - Automatically rotates logs daily.
- **Web Dashboard**:
  - Built with FastAPI and TailwindCSS.
  - View real-time statistics: Total sessions, unique IPs, and recent attack details.
- **Security**:
  - Configurable rate limiting and maximum concurrent sessions.
  - Runs as non-root user (ports > 1024).

## Installation

### Using Docker (Recommended)

1. **Build and Run**:
   ```bash
   docker-compose up -d --build
   ```
   This will start:
   - SSH on port `22` (mapped from 2222)
   - Telnet on port `23` (mapped from 2223)
   - Dashboard on port `8000`

2. **View Dashboard**:
   Open [http://localhost:8000](http://localhost:8000).

3. **View Logs**:
   Logs are mounted to the local `logs/` directory.
   ```bash
   tail -f logs/honeypot-*.jsonl
   ```

### Manual Installation

1. **Prerequisites**: Python 3.9+
2. **Setup**:
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```
3. **Run**:
   ```bash
   python honeypot.py
   # In a separate terminal, start the dashboard
   uvicorn web.app:app --host 0.0.0.0 --port 8000
   ```

## Configuration

Edit `config.yaml` to customize the honeypot:

```yaml
ssh:
  port: 2222          # Internal port
telnet:
  port: 2223          # Internal port

users:                # Valid credentials (for logging 'success')
  - user: "root"
    pass: "P@ssw0rd123"
  - user: "admin"
    pass: "admin"
```

## Project Structure

```
├── honeypot.py              # Main entry point (SSH/Telnet servers)
├── config.yaml              # Configuration file
├── src/
│   ├── core/                # Shell emulation & Fake FS
│   └── utils/               # Logging system
├── web/                     # Web Dashboard (FastAPI)
├── logs/                    # JSON Logs
└── docker-compose.yml       # Docker deployment
```

## License

MIT License
