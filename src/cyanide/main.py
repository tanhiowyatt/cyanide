import asyncio
import signal
import sys
import os
import warnings
import logging
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from cyanide.core import HoneypotServer, load_config

CONFIG_PATH = Path("config/cyanide.cfg")
EASTEREGG_PATH = Path("data/assets/logo.txt")

def is_docker():
    """Detect if running inside a Docker container."""
    return os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER')

def setup_aesthetics(config):
    """Print logo and startup information."""
    # 1. Print Logo
    if EASTEREGG_PATH.exists():
        try:
            print(EASTEREGG_PATH.read_text())
        except Exception:
            pass
    
    # 2. Print Startup Info
    if config:
        print("\n" + "="*50)
        print(" CYANIDE STARTUP INFO")
        print("="*50)
        bind_ip = "0.0.0.0" 
        print(f"[*] Bind Address:   {bind_ip}")
        if config.get('ssh', {}).get('enabled'):
            print(f"[*] SSH Port:       {config['ssh']['port']}")
        if config.get('telnet', {}).get('enabled'):
            print(f"[*] Telnet Port:    {config['telnet']['port']}")
        users = [u['user'] for u in config.get('users', [])]
        print(f"[*] Available Users: {', '.join(users)}")
        print("="*50 + "\n")

async def main():
    """Main entry point."""
    # Silence noise ONLY if NOT in Docker
    if not is_docker():
        warnings.filterwarnings("ignore")
        logging.getLogger('asyncssh').setLevel(logging.ERROR)
        # We don't silence everything here to allow debugging if needed, 
        # but we hide the known noisy ones.
    
    config = load_config(CONFIG_PATH)
    setup_aesthetics(config)
        
    server = HoneypotServer(config)
    
    # Handle signals gracefully
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: sys.exit(0))
        
    print("[*] Starting Cyanide Honeypot...")
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[*] Honeypot stopped.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

