import pytest
import asyncio
import aiohttp

@pytest.mark.asyncio
async def test_http_service(honeypot_server):
    """Test HTTP vulnerable service response."""
    # Using raw socket first to verify headers exactly like original test
    reader, writer = await asyncio.open_connection('127.0.0.1', 8080)
    writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    await writer.drain()
    
    data = await reader.read(1024)
    writer.close()
    await writer.wait_closed()
    
    assert b"200 OK" in data
    assert b"Apache/2.4.41" in data
    assert b"Content-Length" in data

@pytest.mark.asyncio
async def test_mysql_service(honeypot_server):
    """Test MySQL vulnerable service handshake."""
    reader, writer = await asyncio.open_connection('127.0.0.1', 33060)
    
    try:
        data = await reader.read(1024)
        # Check for MariaDB version string in handshake
        assert b"MariaDB" in data
        assert len(data) > 4 # Minimal packet check
    finally:
        writer.close()
        await writer.wait_closed()
