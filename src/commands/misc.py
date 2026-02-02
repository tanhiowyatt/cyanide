import asyncio
import time
from .base import Command

class CurlCommand(Command):
    async def execute(self, args, input_data=""):
        # Fake curl to stdout
        # Just return some dummy HTML
        if not args:
            return "", "curl: try 'curl --help' for more information\n", 1
            
        url = args[-1]
        output = f"<html><body><h1>Fake Response from {url}</h1></body></html>\n"
        return output, "", 0

class PingCommand(Command):
    async def execute(self, args, input_data=""):
        if not args:
             return "", "ping: usage error: Destination address required\n", 2
        
        host = args[0]
        # Simulate just 4 pings
        out = f"PING {host} ({host}) 56(84) bytes of data.\n"
        out += f"64 bytes from {host}: icmp_seq=1 ttl=64 time=0.045 ms\n"
        out += f"64 bytes from {host}: icmp_seq=2 ttl=64 time=0.038 ms\n"
        out += f"64 bytes from {host}: icmp_seq=3 ttl=64 time=0.042 ms\n"
        out += f"64 bytes from {host}: icmp_seq=4 ttl=64 time=0.040 ms\n"
        out += f"\n--- {host} ping statistics ---\n"
        out += "4 packets transmitted, 4 received, 0% packet loss, time 3000ms\n"
        return out, "", 0

class EditorCommand(Command):
    async def execute(self, args, input_data=""):
        # vi/nano mock
        # Simply clear screen and tell user it's a fake editor or just exit
        # Real honeypots might allow editing a temp buffer.
        # For now, just print error or clear screen simulation.
        # But this command is synchronous... 
        # We can't interact. 
        # So we just say "Error: terminal not fully interactive" or similar, 
        # or fake it by printing a "saved" message if a filename is given.
        
        if args:
            filename = args[0]
            # fake save
            return f"Saved {filename}.\n", "", 0
        return "No filename specified.\n", "", 1
