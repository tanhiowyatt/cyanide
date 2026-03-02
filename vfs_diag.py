import asyncio
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path(__file__).parent / "src"))

from cyanide.vfs.engine import FakeFilesystem

def test_vfs():
    fs = FakeFilesystem(os_profile="centos", root_dir="configs/profiles")
    
    print(f"--- Testing VFS for profile: {fs.os_profile} ---")
    
    paths_to_test = ["/", "/bin", "/etc", "/home", "/root", "/var", "/usr", "/usr/bin"]
    
    print("\n[ Directory Check ]")
    for p in paths_to_test:
        print(f"Path: {p:10} | exists: {fs.exists(p)!s:5} | is_dir: {fs.is_dir(p)!s:5}")
        
    print("\n[ list_dir('/') ]")
    print(fs.list_dir("/"))
    
    print("\n[ list_dir('/bin') ]")
    print(fs.list_dir("/bin"))

if __name__ == "__main__":
    test_vfs()
