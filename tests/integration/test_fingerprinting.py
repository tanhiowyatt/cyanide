import asyncio

import pytest

from cyanide.core.server import CyanideServer


@pytest.fixture
def base_config(tmp_path):
    return {
        "ssh": {"enabled": True, "port": 0, "backend_mode": "emulated"},
        "telnet": {"enabled": False},
        "metrics": {"enabled": False},
        "logging": {"directory": str(tmp_path / "logs")},
        "quarantine_path": str(tmp_path / "quarantine"),
        "profiles_dir": "configs/profiles",
        "users": [{"user": "admin", "pass": "admin"}],
    }


async def get_ssh_banner(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        banner = await reader.readline()
        return banner.decode().strip()
    finally:
        writer.close()
        await writer.wait_closed()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "os_type, expected_banner",
    [
        ("ubuntu", "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1"),
        ("debian", "SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1"),
        ("centos", "SSH-2.0-OpenSSH_7.4"),
    ],
)
async def test_ssh_fingerprint(base_config, os_type, expected_banner):
    config = base_config.copy()
    config["os_profile"] = os_type

    server = CyanideServer(config)
    # Ensure profile loader is initialized with the right directory
    server.config["profiles_dir"] = "configs/profiles"

    task = asyncio.create_task(server.start())

    # Wait for server to bind
    port = None
    for _ in range(20):
        if server.ssh_server and server.ssh_server.sockets:
            port = server.ssh_server.sockets[0].getsockname()[1]
            break
        await asyncio.sleep(0.2)

    if port is None:
        await server.stop()
        pytest.fail("Server failed to start and bind to a port")

    try:
        banner = await get_ssh_banner("127.0.0.1", port)
        assert banner == expected_banner
    finally:
        await server.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
