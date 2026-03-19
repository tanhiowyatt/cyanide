import logging
import os
import re
import shlex
from typing import Any

logger = logging.getLogger("cyanide.vfs.scp")


class ScpHandler:
    """
    Simplified SCP protocol handler for honeypot file capture.
    Handles 'sink' mode (-t) which is used for uploading files to the server.
    """

    def __init__(self, session: Any, process: Any = None):
        self.session = session
        self.process = process
        self.honeypot = session.honeypot
        self.fs = getattr(session, "fs", None)
        if not self.fs:
            # Fallback if fs is not directly attached
            self.fs = self.honeypot.get_filesystem(
                session_id=getattr(session, "session_id", "unknown"),
                src_ip=getattr(session, "src_ip", "unknown"),
            )

        self.src_ip = getattr(session, "src_ip", "unknown")
        self.session_id = (
            "conn_" + session.conn_id
            if hasattr(session, "conn_id")
            else getattr(session, "session_id", "unknown")
        )
        self.logger = self.honeypot.logger

    async def _read(self, n: int) -> bytes:
        """Read n bytes from the appropriate input stream."""
        try:
            if self.process is not None:
                # In process_factory mode, use stdin
                data = await self.process.stdin.read(n)
            else:
                # In direct session mode, use channel
                data = await self.session.channel.read(n)

            if isinstance(data, str):
                return data.encode("latin-1")
            return bytes(data)
        except Exception as e:
            logger.error(f"SCP Read Error: {e}")
            return b""

    async def _write(self, data: bytes):
        """Write data to the appropriate output stream."""
        try:
            if self.process is not None:
                # If encoding is set, write() expects a string
                self.process.channel.write(data.decode("latin-1"))
            else:
                self.session.channel.write(data.decode("latin-1"))
        except Exception as e:
            logger.error(f"SCP Write Error: {e}")

    async def _send_ack(self):
        """Send SCP success acknowledgement (a null byte)."""
        await self._write(b"\0")

    async def handle(self, command: str) -> int:
        """
        Main SCP loop.
        Expects a command like 'scp -t /path/to/target'
        """
        is_sink = "-t" in command

        try:
            parts = shlex.split(command)
            dest_dir = parts[-1] if parts else "."
        except Exception:
            dest_dir = "."

        self.logger.log_event(
            self.session_id,
            "scp_exec_detected",
            {
                "command": command,
                "direction": "upload" if is_sink else "download",
                "target_path": dest_dir,
            },
        )

        if not is_sink:
            # For now, we only realistically capture uploads (sink mode)
            # Source mode (-f) for downloads is less common for attackers to use ON us
            return 0

        # Initial ACK to start the protocol
        await self._send_ack()

        while True:
            # Read protocol header (e.g. C0644 123 filename\n)
            header = b""
            while not header.endswith(b"\n"):
                char = await self._read(1)
                if not char:
                    return 0  # Connection closed
                header += char

            header_str = header.decode("utf-8", "ignore").strip()
            if not header_str:
                break

            if header_str.startswith("C"):
                # Cmode size filename
                match = re.match(r"C(\d{4}) (\d+) (.+)", header_str)
                if not match:
                    await self._write(b"\x01SCP Protocol Error: Invalid header\n")
                    return 1

                mode_str, size_str, filename = match.groups()
                size = int(size_str)

                # ACK metadata
                await self._send_ack()

                # Read the actual file content
                content = b""
                remaining = size
                while remaining > 0:
                    chunk = await self._read(min(remaining, 8192))
                    if not chunk:
                        break
                    content += chunk
                    remaining -= len(chunk)

                # Consume the trailing null byte from the client
                await self._read(1)

                # Save to Virtual Filesystem
                target_path = os.path.join(dest_dir, filename)
                if self.fs:
                    try:
                        self.fs.mkfile(
                            target_path,
                            content=content.decode("utf-8", "ignore"),
                            owner=getattr(self.session, "username", "root"),
                            group=getattr(self.session, "username", "root"),
                        )
                    except Exception as e:
                        logger.error(f"Failed to save SCP file to VFS: {e}")

                # Save to Quarantine and Log
                self.honeypot.save_quarantine_file(filename, content, self.session_id, self.src_ip)

                self.logger.log_event(
                    self.session_id,
                    "scp_upload_complete",
                    {"filename": filename, "path": target_path, "size": size, "mode": mode_str},
                )

                # Final ACK for the file
                await self._send_ack()

            elif header_str.startswith("E"):
                # End of directory/transfer
                await self._send_ack()
                break
            else:
                # Unsupported command (T, D, etc. for groups/times)
                # Just ACK to keep the client happy but ignore the data
                await self._send_ack()

        return 0
