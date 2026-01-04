
from pathlib import PurePosixPath
import datetime

class FakeFilesystem:
    """Simulated Linux filesystem for honeypot.
    
    Provides a fake directory structure with pre-populated files and directories
    that mimic a realistic Linux system. Used by ShellEmulator for file operations.
    """
    
    def __init__(self):
        """Initialize fake filesystem with realistic directory structure and files.
        
        Creates common Linux paths including /etc, /var, /proc, /home, and
        populates them with typical configuration files, logs, and honeypot bait.
        """
        self.fs = {
            "/": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/bin": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/etc": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/home": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/home/admin": {"type": "dir", "perm": "drwxr-x---", "owner": "admin", "group": "admin", "size": 4096, "mtime": datetime.datetime.now()},
            "/proc": {"type": "dir", "perm": "dr-xr-xr-x", "owner": "root", "group": "root", "size": 0, "mtime": datetime.datetime.now()},
            "/tmp": {"type": "dir", "perm": "drwxrwxrwt", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/var": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/var/log": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            
            # Files
            "/etc/passwd": {"type": "file", "perm": "-rw-r--r--", "owner": "root", "group": "root", "size": 1234, "content": "root:x:0:0:root:/root:/bin/bash\nadmin:x:1000:1000:admin:/home/admin:/bin/bash\n"},
            "/etc/shadow": {"type": "file", "perm": "-rw-r-----", "owner": "root", "group": "shadow", "size": 842, "content": "root:$6$...\n"},
            "/etc/hostname": {"type": "file", "perm": "-rw-r--r--", "owner": "root", "group": "root", "size": 12, "content": "ubuntu-server\n"},
            "/etc/issue": {"type": "file", "perm": "-rw-r--r--", "owner": "root", "group": "root", "size": 26, "content": "Ubuntu 22.04.3 LTS \\n \\l\n"},
            
            # Fake files
            "/home/admin/file1.txt": {"type": "file", "perm": "-rw-r--r--", "owner": "admin", "group": "admin", "size": 23, "content": "Just a boring file.\n"},
            "/home/admin/secret.conf": {"type": "file", "perm": "-rw-------", "owner": "admin", "group": "admin", "size": 156, "content": "db_password=supersecret123\napi_key=XYZ-999-000\n"},
            "/home/admin/flag.txt": {"type": "file", "perm": "-r--------", "owner": "admin", "group": "admin", "size": 32, "content": "flag{r3al_fl46_f0r_h0n3yp0t}\n"},
            
            # Realistic /proc
            "/proc/cpuinfo": {"type": "file", "perm": "-r--r--r--", "owner": "root", "group": "root", "size": 0, "content": "processor       : 0\nvendor_id       : GenuineIntel\ncpu family      : 6\nmodel           : 142\nmodel name      : Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz\n"},
            "/proc/meminfo": {"type": "file", "perm": "-r--r--r--", "owner": "root", "group": "root", "size": 0, "content": "MemTotal:        8123456 kB\nMemFree:         123456 kB\nBuffers:          23456 kB\nCached:          456789 kB\n"},
            "/proc/version": {"type": "file", "perm": "-r--r--r--", "owner": "root", "group": "root", "size": 0, "content": "Linux version 5.15.0-91-generic (buildd@lcy02-amd64-015) (gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0, GNU ld (GNU Binutils for Ubuntu) 2.38) #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023\n"},

            # Vulnerable Services artifacts
            "/var/www": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/var/www/html": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/var/www/html/index.html": {"type": "file", "perm": "-rw-r--r--", "owner": "www-data", "group": "www-data", "size": 154, "content": "<html><body><h1>It works!</h1><p>Apache Server at 127.0.0.1 Port 80</p></body></html>\n"},
            
            "/var/lib/mysql": {"type": "dir", "perm": "drwxr-x---", "owner": "mysql", "group": "mysql", "size": 4096, "mtime": datetime.datetime.now()},
            
            # Cron
            "/var/spool/cron": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/var/spool/cron/crontabs": {"type": "dir", "perm": "drwx-wx--T", "owner": "root", "group": "crontab", "size": 4096, "mtime": datetime.datetime.now()},
            "/var/spool/cron/crontabs/root": {"type": "file", "perm": "-rw-------", "owner": "root", "group": "crontab", "size": 128, "content": "# m h  dom mon dow   command\n*/5 * * * * /usr/local/bin/backup_secrets.sh\n"},
            
            "/usr/local/bin/backup_secrets.sh": {"type": "file", "perm": "-rwxr-xr-x", "owner": "root", "group": "root", "size": 100, "content": "#!/bin/bash\ntar -czf /tmp/backup.tar.gz /home/admin/secret.conf\n"},

            # User activity
            
            # User activity
            "/var/run": {"type": "dir", "perm": "drwxr-xr-x", "owner": "root", "group": "root", "size": 4096, "mtime": datetime.datetime.now()},
            "/var/run/utmp": {"type": "file", "perm": "-rw-rw-r--", "owner": "root", "group": "utmp", "size": 0, "content": ""}, # Binary file usually, emptiness ok for simple cat, who/w will fake it
        }

    def exists(self, path: str) -> bool:
        return self.resolve(path) in self.fs

    def is_dir(self, path: str) -> bool:
        path = self.resolve(path)
        return self.exists(path) and self.fs[path]["type"] == "dir"

    def is_file(self, path: str) -> bool:
        path = self.resolve(path)
        return self.exists(path) and self.fs[path]["type"] == "file"

    def list_dir(self, path: str) -> list:
        """List contents of a directory.
        
        Args:
            path: Absolute path to directory.
            
        Returns:
            list: List of filenames/directory names in the directory.
                 Returns empty list if path doesn't exist or is not a directory.
        """
        path = self.resolve(path)
        if not self.is_dir(path):
            return []
        
        # Determine direct children
        children = []
        path_depth = len(PurePosixPath(path).parts)
        if path == "/": 
            path_depth = 0 # Root handling
            
        for p in self.fs.keys():
            if p == "/": continue
            pp = PurePosixPath(p)
            # Check if parent matches
            if str(pp.parent) == path or (path == "/" and str(pp.parent) == "/"):
                 # But Ensure we don't pick recursive children if logic is flawed
                 # Using pathlib is better
                 if pp.parent == PurePosixPath(path):
                     children.append(pp.name)
        return sorted(children)

    def get_content(self, path: str) -> str:
        path = self.resolve(path)
        if self.is_file(path):
            return self.fs[path].get("content", "")
        return ""

    def resolve(self, path: str) -> str:
        """Normalize and resolve filesystem path.
        
        Args:
            path: Path to resolve (may contain .., ., //).
            
        Returns:
            str: Normalized absolute path.
            
        Note:
            Handles parent directory (..) and current directory (.) references.
            Removes duplicate slashes and ensures proper path formatting.
        """
        """Resolve path to absolute standard form."""
        # This is a simplified resolver
        if not path.startswith("/"):
            # Assume it's already absolute or caller handles cwd
            pass
        return str(PurePosixPath(path))
