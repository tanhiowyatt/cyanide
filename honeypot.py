
#!/usr/bin/env python3
"""
Advanced SSH/Telnet Honeypot
"""
import asyncio
import asyncssh
import yaml
import sys
import os
import signal
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional

from src.core.fake_filesystem import FakeFilesystem
from src.core.shell_emulator import ShellEmulator
from src.utils.logging_system import HoneypotLogger

CONFIG_PATH = Path("config.yaml")

class HoneypotServer:
    """Main honeypot server orchestrating SSH, Telnet, HTTP, and MySQL services.
    
    This class manages all honeypot services, tracks active sessions, and coordinates
    logging of attacker activity across multiple protocols.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize honeypot server with configuration.
        
        Args:
            config: Configuration dictionary containing service ports,
                   user credentials, session limits, and logging paths.
                   
        Note:
            Checks TEST_LOG_DIR environment variable to override log path during testing.
        """
        self.config = config
        # Use TEST_LOG_DIR if running in test mode
        log_path = os.getenv('TEST_LOG_DIR', config.get("log_path", "logs"))
        self.logger = HoneypotLogger(log_path)
        self.users = self._load_users(config.get("users", []))
        self.active_sessions = 0
        self.max_sessions = config.get("max_sessions", 100)
        self.session_timeout = config.get("session_timeout", 300)

    def _load_users(self, config_users):
        """Load user credentials from configuration.
        
        Args:
            config_users: List of user dictionaries with 'user' and 'pass' keys.
            
        Returns:
            List of user credential dictionaries.
        """
        return config_users

    def is_valid_user(self, username, password):
        """Validate user credentials against configured users.
        
        Args:
            username: Username to validate.
            password: Password to check.
            
        Returns:
            bool: True if credentials match a configured user, False otherwise.
        """
        for user in self.users:
            if user["user"] == username and user["pass"] == password:
                return True
        return False
        
    async def start(self):
        """Start all honeypot services and enter main event loop.
        
        Initializes and starts SSH, Telnet, and optionally HTTP/MySQL services.
        Each service runs in its own async context. The method blocks indefinitely
        until the server is shut down.
        
        Services started:
            - SSH server on configured port (default 2222)
            - Telnet server on configured port (default 2223)
            - HTTP server (if enabled in config)
            - MySQL server (if enabled in config)
        """
        # Generate SSH Host Key
        ssh_key = asyncssh.generate_private_key("ssh-rsa")
        
        # Start SSH Server
        ssh_port = self.config["ssh"]["port"]
        ssh_server = await asyncssh.listen(
            "0.0.0.0", ssh_port,
            server_host_keys=[ssh_key],
            server_factory=lambda: SSHServerFactory(self),
            reuse_address=True
        )
        print(f"[*] SSH Server listening on port {ssh_port}", flush=True)

        # Start Telnet Server
        telnet_port = self.config["telnet"]["port"]
        telnet_server = await asyncio.start_server(
            self.handle_telnet, "0.0.0.0", telnet_port, reuse_address=True
        )
        print(f"[*] Telnet Server listening on port {telnet_port}", flush=True)

        # Start Vulnerable Services
        servers = [ssh_server, telnet_server]
        
        if self.config.get("services", {}).get("http", {}).get("enabled", False):
            http_port = self.config["services"]["http"]["port"]
            http_server = await asyncio.start_server(
                self.handle_http, "0.0.0.0", http_port, reuse_address=True
            )
            print(f"[*] HTTP Server listening on port {http_port}", flush=True)
            servers.append(http_server)

        if self.config.get("services", {}).get("mysql", {}).get("enabled", False):
            mysql_port = self.config["services"]["mysql"]["port"]
            mysql_server = await asyncio.start_server(
                self.handle_mysql, "0.0.0.0", mysql_port, reuse_address=True
            )
            print(f"[*] MySQL Server listening on port {mysql_port}", flush=True)
            servers.append(mysql_server)

        # Keep running
        # Python 3.9 compatibility: Use gather instead of TaskGroup
        from contextlib import AsyncExitStack
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(ssh_server)
            await stack.enter_async_context(telnet_server)
            if 'http_server' in locals(): await stack.enter_async_context(http_server)
            if 'mysql_server' in locals(): await stack.enter_async_context(mysql_server)
            
            # Wait forever
            await asyncio.Future()

    async def handle_http(self, reader, writer):
        """Handle HTTP connections and serve fake Apache default page.
        
        Args:
            reader: AsyncIO stream reader for incoming data.
            writer: AsyncIO stream writer for outgoing responses.
            
        Note:
            Logs connection attempt and serves Apache 2.4.41 banner with default page.
            Connection timeout is 5 seconds.
        """
        src_ip, src_port = writer.get_extra_info("peername")
        session_id = str(uuid.uuid4())[:8]
        try:
            # Read request
            request = await asyncio.wait_for(reader.read(1024), timeout=5)
            await self.logger.log_event({
                "event": "connect", "protocol": "http", "src_ip": src_ip, "src_port": src_port, 
                "session_id": session_id, "request_preview": request.decode(errors="ignore").splitlines()[0] if request else ""
            })
            
            # Send Apache default page header
            body = "<html><body><h1>It works!</h1><p>Apache Server at 127.0.0.1 Port 80</p></body></html>"
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT") + "\r\n"
                "Server: Apache/2.4.41 (Ubuntu)\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                f"{body}"
            )
            writer.write(response.encode())
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()

    async def handle_mysql(self, reader, writer):
        """Handle MySQL connections with fake MariaDB handshake.
        
        Args:
            reader: AsyncIO stream reader for incoming data.
            writer: AsyncIO stream writer for outgoing responses.
            
        Note:
            Sends fake MariaDB 10.4.13 handshake packet followed by access denied error.
            Logs connection attempt with source IP.
        """
        src_ip, src_port = writer.get_extra_info("peername")
        session_id = str(uuid.uuid4())[:8]
        try:
             await self.logger.log_event({
                "event": "connect", "protocol": "mysql", "src_ip": src_ip, "src_port": src_port, "session_id": session_id
            })
             # Fake MySQL Handshake (Version 5.5.5-10.4.13-MariaDB)
             # Packet structure: length (3), seq(1), protocol(1), version(str), thread(4), salt(8), caps(2), charset(1), status(2), caps(2), len(1), salt(12)
             # Simplified payload
             # 5a 00 00 00 0a 35 2e 35 2e 35 2d 31 30 2e 34 2e 31 33 2d 4d 61 72 69 61 44 42 00 ...
             
             # Constructing valid handshake packet
             proto_ver = b'\x0a'
             server_ver = b'5.5.5-10.4.13-MariaDB\x00'
             thread_id = b'\x00\x00\x00\x01'
             salt = b'12345678'
             caps = b'\x00\x42'
             
             payload = proto_ver + server_ver + thread_id + salt + b'\x00' + caps + b'\x21\x00\x00' + b'\x00'*13 + b'123456789012\x00'
             
             # Header: length (little endian) + seq
             length = len(payload)
             header = length.to_bytes(3, 'little') + b'\x00'
             
             writer.write(header + payload)
             await writer.drain()
             
             # Read login attempt
             await asyncio.wait_for(reader.read(1024), timeout=5)
             
             # Send Access Denied
             # Packet: len, seq, 0xFF (err), err_code, marker, message
             msg = b'Access denied for user \'root\'@\'' + src_ip.encode() + b'\''
             err_payload = b'\xff\x15\x04#28000' + msg
             err_header = len(err_payload).to_bytes(3, 'little') + b'\x02' # Seq 2 usually
             
             writer.write(err_header + err_payload)
             await writer.drain()
             
        except Exception:
            pass
        finally:
             writer.close()

    async def handle_telnet(self, reader, writer):
        """Handle Telnet connections with interactive shell emulation.
        
        Args:
            reader: AsyncIO stream reader for incoming data.
            writer: AsyncIO stream writer for outgoing responses.
            
        Note:
            Implements full Telnet login flow with username/password prompt.
            Provides fake shell with command execution logging.
            Enforces max_sessions limit and session_timeout.
        """
        if self.active_sessions >= self.max_sessions:
            writer.close()
            return
            
        self.active_sessions += 1
        session_id = str(uuid.uuid4())[:8]
        src_ip, src_port = writer.get_extra_info("peername")
        start_time = time.time()
        
        commands = []
        username = ""
        password = ""
        
        try:
            await self.logger.log_event({
                "event": "connect", "protocol": "telnet", 
                "src_ip": src_ip, "src_port": src_port, "session_id": session_id
            })
            
            # Simple auth
            writer.write(b"login: ")
            await writer.drain()
            username = (await reader.readuntil(b"\n")).decode().strip()
            
            writer.write(b"Password: ")
            await writer.drain()
            password = (await reader.readuntil(b"\n")).decode().strip()
            
            success = self.is_valid_user(username, password)
            await self.logger.log_event({
                "event": "auth", "protocol": "telnet", "session_id": session_id,
                "src_ip": src_ip, "username": username, "password": password, "success": success
            })
            
            # Shell loop
            writer.write(b"\r\nWelcome to Ubuntu 22.04.3 LTS\r\n\r\n")
            
            fs = FakeFilesystem()
            shell = ShellEmulator(fs, username if success else "user")
            
            prompt = f"{username}@server:~$ "
            writer.write(prompt.encode())
            await writer.drain()
            
            while True:
                try:
                    line = await asyncio.wait_for(reader.readuntil(b"\n"), timeout=self.session_timeout)
                    cmd = line.decode().strip()
                    if not cmd:
                        writer.write(prompt.encode())
                        await writer.drain()
                        continue
                        
                    commands.append(cmd)
                    
                    if cmd in ("exit", "logout"):
                        break
                        
                    # Log command immediately
                    await self.logger.log_command(session_id, "telnet", src_ip, username, cmd, client_version="Telnet")

                    stdout, stderr, rc = shell.execute(cmd)
                    output = stdout + stderr
                    writer.write(output.replace("\n", "\r\n").encode())
                    writer.write(prompt.encode())
                    await writer.drain()
                    
                except asyncio.TimeoutError:
                    writer.write(b"\r\nTimeout.\r\n")
                    break
        except Exception as e:
            pass
        finally:
            duration = time.time() - start_time
            await self.logger.log_event({
                "event": "session_end", "protocol": "telnet", "session_id": session_id,
                "src_ip": src_ip, "username": username, "commands": commands, "duration": duration
            })
            self.active_sessions -= 1
            writer.close()

class SSHServerFactory(asyncssh.SSHServer):
    """SSH server factory for creating SSH sessions and handling authentication.
    
    Tracks connection metadata and validates passwords against configured users.
    Logs all authentication attempts regardless of success.
    """
    
    def __init__(self, honeypot: HoneypotServer):
        """Initialize SSH server factory.
        
        Args:
            honeypot: Parent HoneypotServer instance for accessing config and logging.
        """
        self.honeypot = honeypot
        self.src_ip = None
        self.src_port = None
    
    def connection_made(self, conn):
        """Called when SSH connection is established.
        
        Args:
            conn: AsyncSSH connection object containing peer information.
        """
        self.src_ip = conn.get_extra_info("peername")[0]
        self.src_port = conn.get_extra_info("peername")[1]
        
    def password_auth_supported(self):
        """Indicate that password authentication is supported.
        
        Returns:
            bool: Always returns True to accept password auth attempts.
        """
        return True
        
    def validate_password(self, username, password):
        """Validate SSH password and log authentication attempt.
        
        Args:
            username: Username provided by client.
            password: Password provided by client.
            
        Returns:
            bool: Always returns True to keep connection alive for honeypot purposes.
            
        Note:
            Logs authentication attempt with success/failure status but always
            accepts the connection to observe attacker behavior.
        """
        # We accept everyone but log success based on config
        success = self.honeypot.is_valid_user(username, password)
        asyncio.create_task(self.honeypot.logger.log_event({
            "event": "auth", "protocol": "ssh", 
            "src_ip": self.src_ip, "username": username, "password": password, "success": success
        }))
        return True

    def session_requested(self):
        return SSHSession(self.honeypot, self.src_ip, self.src_port)

class SSHSession(asyncssh.SSHServerSession):
    """SSH session handler for interactive and exec-style command execution.
    
    Manages individual SSH sessions, providing fake shell interaction and logging
    all commands executed by the attacker. Handles both interactive shells and
    single command execution (ssh user@host command).
    """
    
    def __init__(self, honeypot: HoneypotServer, src_ip, src_port):
        """Initialize SSH session.
        
        Args:
            honeypot: Parent HoneypotServer instance.
            src_ip: Source IP address of the connection.
            src_port: Source port of the connection.
        """
        self.honeypot = honeypot
        self.src_ip = src_ip
        self.src_port = src_port
        self.session_id = str(uuid.uuid4())[:8]
        self.commands = []
        self.start_time = time.time()
        self.client_version = "unknown"
        self.username = "root"
        self.buf = ""
        self.fs = None
        self.shell = None
        self.prompt = None 
        
    def connection_made(self, channel):
        """Called when SSH channel is established.
        
        Args:
            channel: AsyncSSH channel object.
            
        Note:
            Extracts username and SSH client version from connection metadata.
        """
        self.channel = channel
        self.username = channel.get_connection().get_extra_info("username") or "root"
        self.client_version = channel.get_connection().get_extra_info("client_version") or "unknown"

    def shell_requested(self):
        """Handle interactive shell request from SSH client.
        
        Returns:
            bool: Always returns True to indicate shell is available.
            
        Note:
            Initializes shell emulator for interactive session.
        """
        self.fs = FakeFilesystem()
        self.shell = ShellEmulator(self.fs, self.username)
        self.prompt = f"{self.username}@server:~$ "
        return True
    
    def session_started(self):
        """Called when SSH session channel is fully open.
        
        Note:
            Sends welcome message and initial prompt to client.
        """
        self.channel.write(f"Welcome into {self.username} shell\r\n")
        self.channel.write(self.prompt)
    
    def data_received(self, data, datatype=None):
        """Called when data is received from SSH client.
        
        Args:
            data: Data received (bytes or str).
            datatype: Extended data type (unused).
            
        Note:
            Main input handler - processes commands line by line.
        """
        try:
            # Decode if bytes
            if isinstance(data, bytes):
                data = data.decode('utf-8', errors='ignore')
            
            self.buf += data
            
            # Process complete lines
            while "\n" in self.buf or "\r" in self.buf:
                if "\n" in self.buf:
                    line, self.buf = self.buf.split("\n", 1)
                elif "\r" in self.buf:
                    line, self.buf = self.buf.split("\r", 1)
                else:
                    break
                    
                cmd = line.strip()
                if not cmd:
                    self.channel.write("\r\n" + self.prompt)
                    continue
                    
                self.commands.append(cmd)
                
                # Handle exit
                if cmd in ("exit", "logout"):
                    asyncio.create_task(self._close_session())
                    return
                
                # Log and execute
                asyncio.create_task(self.honeypot.logger.log_command(
                    self.session_id, "ssh", self.src_ip, self.username, cmd,
                    client_version=self.client_version
                ))
                
                stdout, stderr, rc = self.shell.execute(cmd)
                self.channel.write("\r\n" + stdout + stderr)
                self.channel.write(self.prompt)
                
        except Exception as e:
            print(f"[DEBUG] data_received error: {e}", flush=True)
    
    async def _close_session(self):
        """Helper to gracefully close session."""
        await asyncio.sleep(0.01)
        self.channel.write_eof()
        self.channel.exit(0)
        self.channel.close()

    def exec_requested(self, command):
        """Handle single command execution request (ssh user@host command).
        
        Args:
            command: Command string to execute.
            
        Returns:
            bool: Always returns True to indicate command execution is supported.
            
        Note:
            Logs the command and executes it in fake shell environment.
        """
        # Handle exec (ssh user@host command)
        print(f"[DEBUG] exec_requested: {command}", flush=True)
        self.commands.append(command)
        asyncio.create_task(self.honeypot.logger.log_command(
            self.session_id, "ssh", self.src_ip, self.username, command,
            client_version=self.client_version
        ))
        asyncio.create_task(self._async_exec(command))
        return True

    async def _async_exec(self, command):
        fs = FakeFilesystem()
        shell = ShellEmulator(fs, self.username)
        stdout, stderr, rc = shell.execute(command)
        self.channel.write(stdout)
        self.channel.write_stderr(stderr)
        self.channel.write_eof()
        # await self.channel.drain() # drain might not be available on channel, checking asyncssh docs
        # asyncssh channel write is not awaitable directly usually, but let's try just yielding
        await asyncio.sleep(0.01)
        self.channel.exit(rc)
        self.channel.close()


                
    def session_ended(self):
        duration = time.time() - self.start_time
        asyncio.create_task(self.honeypot.logger.log_event({
            "event": "session_end", "protocol": "ssh", "session_id": self.session_id,
            "src_ip": self.src_ip, "username": self.username, "commands": self.commands, "duration": duration,
            "client_version": self.client_version
        }))

async def main():
    if not CONFIG_PATH.exists():
        print("Config not found")
        sys.exit(1)
        
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
        
    server = HoneypotServer(config)
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: sys.exit(0))
        
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
