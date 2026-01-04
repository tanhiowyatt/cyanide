
import shlex
import time
from .fake_filesystem import FakeFilesystem

class ShellEmulator:
    """Fake Linux shell emulator for honeypot command execution.
    
    Provides realistic command execution behavior including filesystem navigation,
    file reading, process listing, and other common Linux commands. All operations
    are performed against a fake filesystem.
    """
    
    def __init__(self, fs: FakeFilesystem, username: str = "root"):
        """Initialize shell emulator with filesystem and user context.
        
        Args:
            fs: FakeFilesystem instance for file operations.
            username: Username for the session (affects paths and permissions).
        """
        self.fs = fs
        self.username = username
        self.cwd = "/home/admin" if username == "admin" else "/root" if username == "root" else f"/home/{username}"
        if not self.fs.exists(self.cwd):
            self.cwd = "/"

    def resolve_path(self, path: str) -> str:
        """Resolve relative or absolute path to filesystem path.
        
        Args:
            path: Path to resolve (absolute or relative to cwd).
            
        Returns:
            str: Resolved absolute path in filesystem.
        """
        if path.startswith("/"):
            return self.fs.resolve(path)
        return self.fs.resolve(f"{self.cwd}/{path}")

    def execute(self, command_line: str) -> tuple[str, str, int]:
        """Execute a shell command and return output.
        
        Args:
            command_line: Complete command line string to parse and execute.
            
        Returns:
            tuple: (stdout, stderr, return_code) where:
                - stdout: Standard output from command
                - stderr: Standard error from command  
                - return_code: Exit code (0 for success, >0 for error)
                
        Note:
            Supports common Linux commands: cd, ls, pwd, cat, whoami, id,
            echo, uname, ps, sudo, export, who, w.
        """
        if not command_line.strip():
            return "", "", 0

        try:
            args = shlex.split(command_line)
        except ValueError:
            return "", "Syntax error\n", 1

        cmd = args[0]
        params = args[1:]

        if cmd == "cd":
            return self._cd(params)
        elif cmd == "ls" or cmd == "dir":
            return self._ls(params)
        elif cmd == "pwd":
            return f"{self.cwd}\n", "", 0
        elif cmd == "cat":
            return self._cat(params)
        elif cmd == "whoami":
            return f"{self.username}\n", "", 0
        elif cmd == "id":
            uid = 0 if self.username == "root" else 1000
            gid = 0 if self.username == "root" else 1000
            return f"uid={uid}({self.username}) gid={gid}({self.username}) groups={gid}({self.username})\n", "", 0
        elif cmd == "echo":
            return " ".join(params) + "\n", "", 0
        elif cmd == "uname":
            if "-a" in params:
                return "Linux ubuntu-server 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux\n", "", 0
            return "Linux\n", "", 0
        elif cmd == "ps":
            return self._ps(params)
        elif cmd == "sudo":
            return self._sudo(params)
        elif cmd == "help":
            return "GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)\nThese shell commands are defined internally.  Type `help' to see this list.\n", "", 0
        elif cmd == "export":
            return self._export(params)
        elif cmd == "who":
            return self._who(params)
        elif cmd == "w":
            return self._w(params)
        else:
            return "", f"{cmd}: command not found\n", 127

    def _cd(self, args):
        """Change current working directory.
        
        Args:
            args: List of command arguments (directory path).
            
        Returns:
            tuple: (stdout, stderr, return_code)
        """
        if not args:
            target = "/root" if self.username == "root" else f"/home/{self.username}"
        else:
            target = self.resolve_path(args[0])
        
        if self.fs.is_dir(target):
            self.cwd = target
            return "", "", 0
        return "", f"cd: {args[0]}: No such file or directory\n", 1

    def _ls(self, args):
        """List directory contents.
        
        Args:
            args: List of command arguments (optional directory path).
            
        Returns:
            tuple: (stdout, stderr, return_code)
            
        Note:
            Returns space-separated list of filenames.
        """
        target = self.cwd
        if args and not args[0].startswith("-"):
            target = self.resolve_path(args[0])
        
        children = self.fs.list_dir(target)
        if not children and not self.fs.is_dir(target):
             return "", f"ls: cannot access '{args[0]}': No such file or directory\n", 2
             
        # Simple output format
        return "  ".join(children) + "\n", "", 0

    def _cat(self, args):
        """Display file contents.
        
        Args:
            args: List of file paths to display.
            
        Returns:
            tuple: (stdout, stderr, return_code)
            
        Note:
            Supports basic wildcard matching for 'flag*' patterns.
        """
        if not args:
            return "", "", 0
        
        output = ""
        for arg in args:
            if "*" in arg: 
                # Very basic wildcard handling for flag*
                if "flag" in arg:
                    # Look for flag in cwd
                    files = self.fs.list_dir(self.cwd)
                    for f in files:
                        if "flag" in f:
                            output += self.fs.get_content(f"{self.cwd}/{f}")
                continue

            path = self.resolve_path(arg)
            if self.fs.is_file(path):
                output += self.fs.get_content(path)
            elif self.fs.is_dir(path):
                return "", f"cat: {arg}: Is a directory\n", 1
            else:
                return "", f"cat: {arg}: No such file or directory\n", 1
        return output, "", 0

    def _ps(self, args):
        """Display fake process list.
        
        Args:
            args: Command arguments (ignored).
            
        Returns:
            tuple: (stdout, stderr, return_code)
        """
        # Fake process list
        output = "    PID TTY          TIME CMD\n"
        output += f"   {1234} pts/0    00:00:00 bash\n"
        output += f"   {1235} pts/0    00:00:00 ps\n"
        return output, "", 0

    def _sudo(self, args):
        """Simulate sudo command with password failure.
        
        Args:
            args: Command arguments (ignored).
            
        Returns:
            tuple: (stdout, stderr, return_code)
            
        Note:
            Always returns password failure after 3 attempts.
        """
        return "", f"[sudo] password for {self.username}: \nSorry, try again.\n[sudo] password for {self.username}: \nsudo: 3 incorrect password attempts\n", 1

    def _export(self, args):
        """Handle environment variable export (no-op).
        
        Args:
            args: Variable assignment arguments.
            
        Returns:
            tuple: (stdout, stderr, return_code)
            
        Note:
            Accepts export commands silently without actually setting variables.
            This prevents errors from SSH client initialization scripts.
        """
        # Allow export command but do nothing (fake success)
        # Often SSH clients send 'export LANG=...' on startup
        return "", "", 0

    def _who(self, args):
        """Display fake list of logged-in users.
        
        Args:
            args: Command arguments (ignored).
            
        Returns:
            tuple: (stdout, stderr, return_code)
            
        Note:
            Shows fake users 'root' and 'admin' with realistic timestamps and IPs.
        """
        # Fake output compatible with typical 'who'
        now = time.strftime("%Y-%m-%d %H:%M")
        return f"root     pts/0        {now} (192.168.1.50)\nadmin    pts/1        {now} (10.0.0.2)\n", "", 0

    def _w(self, args):
        """Display who is logged in and what they are doing.
        
        Args:
            args: Command arguments (ignored).
            
        Returns:
            tuple: (stdout, stderr, return_code)
            
        Note:
            Shows uptime, load average, and user activity simulation.
        """
        now = time.strftime("%H:%M:%S")
        return f" {now} up 12 days, 14:10,  2 users,  load average: 0.01, 0.03, 0.00\nUSER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\nroot     pts/0    192.168.1.50     09:00    1.00s  0.10s  0.00s w\nadmin    pts/1    10.0.0.2         10:30    2:00   0.05s  0.01s bash\n", "", 0
