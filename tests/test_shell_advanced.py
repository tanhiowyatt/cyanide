
import pytest
from src.core.fake_filesystem import FakeFilesystem
from src.core.shell_emulator import ShellEmulator

@pytest.fixture
def shell():
    fs = FakeFilesystem()
    return ShellEmulator(fs, "root")

def test_chaining_and(shell):
    # true && echo success
    # 'true' command doesn't exist, we might need to mock it or use 'echo'
    # Wait, simple 'echo' returns 0.
    # echo "1" && echo "2"
    stdout, stderr, rc = shell.execute('echo "1" && echo "2"')
    assert "1" in stdout
    assert "2" in stdout
    assert rc == 0

def test_chaining_or_fail(shell):
    # false || echo "recovered"
    # we don't have 'false'. Let's use a non-existent command
    stdout, stderr, rc = shell.execute('badcmd || echo "recovered"')
    assert "command not found" in stderr
    assert "recovered" in stdout
    # The last command determines RC? Yes.
    assert rc == 0

def test_chaining_or_skip(shell):
    # echo "ok" || echo "skip"
    stdout, stderr, rc = shell.execute('echo "ok" || echo "skip"')
    assert "ok" in stdout
    assert "skip" not in stdout
    assert rc == 0

def test_redirection_write(shell):
    shell.execute('echo "content" > /test.txt')
    assert shell.fs.get_content('/test.txt') == "content\n" 
    # echo adds \n usually? Let's check EchoCommand implementation later.
    # Usually echo does add \n.

def test_redirection_append(shell):
    shell.execute('echo "line1" > /test.txt')
    shell.execute('echo "line2" >> /test.txt')
    content = shell.fs.get_content('/test.txt')
    assert "line1" in content
    assert "line2" in content

def test_pipe_simple(shell):
    # cat file | cat
    shell.execute('echo "piped" > /source.txt')
    stdout, _, _ = shell.execute('cat /source.txt | cat')
    assert "piped" in stdout

def test_pipe_chain(shell):
    # echo "data" | cat | cat
    # echo usually prints to stdout. 
    # We need to ensure logic: echo out -> cat in -> cat out
    stdout, _, _ = shell.execute('echo "data" | cat | cat')
    # echo output is "data\n"
    # cat reads stdin. We need to verify 'cat' supports stdin.
    assert "data" in stdout

def test_complex_scenario(shell):
    # echo "hack" > /tmp/malware && cat /tmp/malware | cat >> /var/log/hacked
    shell.execute('echo "hack" > /tmp/malware && cat /tmp/malware | cat >> /var/log/hacked')
    assert shell.fs.get_content('/var/log/hacked') == "hack\n"

