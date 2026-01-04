import pytest
import asyncio

@pytest.mark.asyncio
async def test_telnet_login_flow(honeypot_server):
    """Test full Telnet login and command execution flow."""
    reader, writer = await asyncio.open_connection('127.0.0.1', 2223)
    
    try:
        # Login
        await reader.readuntil(b"login: ")
        writer.write(b"admin\n")
        await writer.drain()
        
        # Password
        await reader.readuntil(b"Password: ")
        writer.write(b"admin\n")
        await writer.drain()
        
        # Prompt
        data = await asyncio.wait_for(reader.readuntil(b"$ "), timeout=5)
        assert b"Welcome" in data or b"admin@server:~$" in data

        # Command
        writer.write(b"whoami\n")
        await writer.drain()
        
        data = await asyncio.wait_for(reader.readuntil(b"$ "), timeout=2)
        assert b"admin" in data
        
        # Exit
        writer.write(b"exit\n")
        await writer.drain()
        
    finally:
        writer.close()
        await writer.wait_closed()
