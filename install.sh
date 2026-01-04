
#!/bin/bash
set -e

echo "[*] Installing dependencies..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "[*] Creating service file..."
sudo tee /etc/systemd/system/honeypot.service << EOF
[Unit]
Description=Advanced SSH/Telnet Honeypot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/.venv/bin/python3 honeypot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "[*] Reloading systemd..."
sudo systemctl daemon-reload

echo "[*] Installation complete."
echo "To start: sudo systemctl start honeypot"
echo "To view logs: tail -f logs/honeypot-*.jsonl"
