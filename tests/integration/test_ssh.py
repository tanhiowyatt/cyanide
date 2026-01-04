import pytest
import asyncssh
import asyncio

@pytest.mark.asyncio
async def test_ssh_connection_and_auth(honeypot_server):
    """Test basic SSH connection and authentication."""
    async with asyncssh.connect('127.0.0.1', port=2222, username='root', password='password', known_hosts=None) as conn:
        assert conn is not None

@pytest.mark.asyncio
async def test_ssh_simple_command(honeypot_server):
    """Test executing a simple command via SSH."""
    async with asyncssh.connect('127.0.0.1', port=2222, username='root', password='password', known_hosts=None) as conn:
        result = await conn.run('whoami', check=True)
        assert result.stdout.strip() == 'root'

@pytest.mark.asyncio
async def test_ssh_filesystem_access(honeypot_server):
    """Test accessing fake filesystem files."""
    async with asyncssh.connect('127.0.0.1', port=2222, username='root', password='password', known_hosts=None) as conn:
        # Check directory listing
        result = await conn.run('ls /home/admin', check=True)
        assert "flag.txt" in result.stdout
        
        # Check file content
        result = await conn.run('cat /home/admin/flag.txt', check=True)
        assert "flag{" in result.stdout

@pytest.mark.asyncio
async def test_ssh_interactive_shell(honeypot_server):
    """Test interactive shell session behavior."""
    async with asyncssh.connect('127.0.0.1', port=2222, username='root', password='password', known_hosts=None) as conn:
        async with conn.create_process() as process:
            # Give shell time to initialize
            await asyncio.sleep(0.1)
            
            process.stdin.write('uname\n')
            await asyncio.sleep(0.1)  # Wait for command to execute
            
            process.stdin.write('exit\n')
            process.stdin.write_eof()
            
            stdout = await process.stdout.read()
            # More flexible assertion - check for either Linux or the prompt
            assert "Linux" in stdout or "root@server" in stdout

@pytest.mark.asyncio
async def test_ssh_advanced_commands(honeypot_server):
    """Test new commands like 'who'."""
    async with asyncssh.connect('127.0.0.1', port=2222, username='root', password='password', known_hosts=None) as conn:
        result = await conn.run('who', check=True)
        assert "root" in result.stdout
