import pytest
import asyncio
import threading
import time
import os
import signal
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from honeypot import HoneypotServer
import yaml

CONFIG_PATH = Path("config.yaml")

@pytest.fixture(scope="session")
def honeypot_server():
    """Start the honeypot server in a separate process for the session."""
    config_path = Path("config.yaml").resolve()
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Check if ports are available first, kill if needed
    os.system(f"lsof -t -i :{config['ssh']['port']} | xargs kill -9 2>/dev/null || true")
    os.system(f"lsof -t -i :{config['telnet']['port']} | xargs kill -9 2>/dev/null || true")
    os.system(f"lsof -t -i :8080 | xargs kill -9 2>/dev/null || true")
    os.system(f"lsof -t -i :33060 | xargs kill -9 2>/dev/null || true")
    
    # Start server as subprocess
    import subprocess
    
    log_dir = Path("logs/logs_tests")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variable to redirect honeypot logs to /tmp during tests
    # This keeps logs/logs_tests clean for pytest output only
    env = os.environ.copy()
    env['TEST_LOG_DIR'] = '/tmp/honeypot_test_logs'
    
    with open(log_dir / "test_server.log", "w") as log_file:
        process = subprocess.Popen(
            [sys.executable, "honeypot.py"],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=str(Path(".").resolve()),
            env=env
        )
    
    start_time = time.time()
    created = False
    while time.time() - start_time < 10:
        import socket
        try:
            with socket.create_connection(("127.0.0.1", config['ssh']['port']), timeout=0.1):
                created = True
                break
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
            
    if not created:
         process.kill()
         print("Timeout waiting for server to start.")
         raise RuntimeError("Server failed to start")
            
    yield process
    
    try:
        process.terminate()
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
