from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from cyanide.vfs.engine import FakeFilesystem
from cyanide.vfs.scp import ScpHandler


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.honeypot = MagicMock()
    session.honeypot.config = {"ssh": {"allow_upload": True}}
    session.honeypot.logger = MagicMock()
    session.honeypot.save_quarantine_file = MagicMock()
    session.fs = FakeFilesystem()
    session.src_ip = "1.2.3.4"
    session.conn_id = "test_conn"
    session.username = "root"
    return session


@pytest.fixture
def mock_process():
    process = MagicMock()
    process.stdin = AsyncMock()
    process.channel = MagicMock()
    return process


@pytest.mark.asyncio
async def test_scp_upload_sink_mode(mock_session, mock_process):
    handler = ScpHandler(mock_session, process=mock_process)
    mock_session.fs.mkdir_p("/tmp")

    # Simulate SCP sink protocol for a file named 'malware.sh' with content 'echo hi'
    metadata = b"C0644 7 malware.sh\n"
    content = b"echo hi"

    # Sequence of reads:
    # 1. First header
    # 2. Content
    # 3. Trailing null
    # 4. E (End of transfer)
    mock_process.stdin.read.side_effect = [
        metadata,  # Metadata header
        content,  # File content
        b"\0",  # Trailing null from client
        b"E\n",  # End command
        b"",  # End of stream
    ]

    rc = await handler.handle("scp -t /tmp")

    assert rc == 0
    # Verify file created in VFS
    assert mock_session.fs.exists("/tmp/malware.sh")
    assert mock_session.fs.get_content("/tmp/malware.sh") == "echo hi"

    # Verify logging and quarantine
    mock_session.honeypot.save_quarantine_file.assert_called_with(
        "malware.sh", b"echo hi", "conn_test_conn", "1.2.3.4"
    )
    mock_session.honeypot.logger.log_event.assert_any_call(
        "conn_test_conn", "scp_upload_complete", ANY
    )


@pytest.mark.asyncio
async def test_scp_upload_invalid_header(mock_session, mock_process):
    handler = ScpHandler(mock_session, process=mock_process)

    mock_process.stdin.read.side_effect = [b"XINVALID\n", b""]

    rc = await handler.handle("scp -t /tmp")
    # It should just exit or handle normally
    assert rc == 0
    # Should have sent an ACK for the initial connection then ignore or ACK the invalid line
    assert mock_process.channel.write.call_count >= 1
