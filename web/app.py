
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import glob
from operator import itemgetter

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")

LOG_DIR = Path("logs")

@app.get("/")
async def index(request: Request):
    # Read logs
    stats = {
        "total_sessions": 0,
        "unique_ips": set(),
        "ssh_count": 0,
        "telnet_count": 0,
        "top_commands": {}
    }
    
    recent_sessions = []
    
    log_files = sorted(glob.glob(str(LOG_DIR / "honeypot-*.jsonl")), reverse=True)
    
    # Analyze last 2 files for performance
    for log_file in log_files[:2]:
        try:
            with open(log_file) as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        event = data.get("event")
                        
                        if event == "connect":
                            stats["total_sessions"] += 1
                            stats["unique_ips"].add(data.get("src_ip"))
                            if data.get("protocol") == "ssh": stats["ssh_count"] += 1
                            if data.get("protocol") == "telnet": stats["telnet_count"] += 1
                            
                        if event == "session_end":
                            recent_sessions.append(data)
                            
                        # Basic command stats
                        if event == "command":
                            cmd = data.get("command")
                            stats["top_commands"][cmd] = stats["top_commands"].get(cmd, 0) + 1
                    except:
                        pass
        except:
             pass

    recent_sessions.sort(key=itemgetter("timestamp"), reverse=True)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "stats": {
            "total_sessions": stats["total_sessions"],
            "unique_ips": len(stats["unique_ips"]),
            "ssh_count": stats["ssh_count"],
            "telnet_count": stats["telnet_count"]
        },
        "recent_sessions": recent_sessions[:50]
    })
