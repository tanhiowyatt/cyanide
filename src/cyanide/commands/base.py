import socket
import ipaddress
from urllib.parse import urlparse
class Command:
    """Base class for shell commands."""
    
    def __init__(self, emulator):
        self.emulator = emulator
        self.fs = emulator.fs
        self.username = emulator.username

    async def execute(self, args: list[str], input_data: str = "") -> tuple[str, str, int]:
        """Execute the command asynchronously.
        
        Args:
            args: Command arguments (excluding command name).
            input_data: Input from stdin (e.g. from pipe).
            
        Returns:
            tuple: (stdout, stderr, return_code)
        """
        raise NotImplementedError

    def validate_url(self, url: str) -> tuple[bool, str]:
        """Validate URL to prevent SSRF and local file access.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False, f"Protocol '{parsed.scheme}' not supported or disabled."
                
            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid URL"
                
            # Resolve to IP
            try:
                ip_list = socket.getaddrinfo(hostname, None)
                # Check first IP
                ip_str = ip_list[0][4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                
                # Check config
                allow_local = self.emulator.config.get("allow_local_network", False) if hasattr(self.emulator, "config") else False
                
                if not allow_local and (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local):
                    return False, f"Access to private/local resource '{hostname}' ({ip_str}) denied."
                    
            except socket.gaierror:
                return False, f"Could not resolve host: {hostname}"
                
            return True, ""
        except ValueError:
            return False, "Invalid URL format"
        except Exception as e:
            return False, f"URL validation error: {e}"
