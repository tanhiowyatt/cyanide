import argparse
from .base import Command

class TextOpCommand(Command):
    """Base for text operations."""
    pass

class GrepCommand(TextOpCommand):
    async def execute(self, args, input_data=""):
        # Simplified grep: only supports finding fixed string
        if not args:
            return "", "grep: usage: grep [PATTERN] [FILE...]\n", 2
            
        pattern = args[0]
        files = args[1:]
        
        lines = []
        if not files:
            # Read from input_data
            lines = input_data.splitlines(keepends=True)
        else:
            for f in files:
                path = self.emulator.resolve_path(f)
                if self.fs.is_file(path):
                     content = self.fs.get_content(path)
                     lines.extend(content.splitlines(keepends=True))
                # Skip dirs/errors for simplicity like real grep (unless -s) except usually grep prints error.
        
        output = ""
        for line in lines:
            if pattern in line:
                output += line
                
        # grep returns 0 if found, 1 if not found
        rc = 0 if output else 1
        return output, "", rc

class HeadCommand(TextOpCommand):
    async def execute(self, args, input_data=""):
        parser = argparse.ArgumentParser(prog="head", add_help=False)
        parser.add_argument("-n", "--lines", type=int, default=10)
        parser.add_argument("files", nargs="*")
        
        try:
            parsed, unknown = parser.parse_known_args(args)
        except SystemExit:
            return "", "", 1
            
        count = parsed.lines
        files = parsed.files
        
        lines = []
        if not files:
            lines = input_data.splitlines(keepends=True)
        else:
            path = self.emulator.resolve_path(files[0])
            if self.fs.is_file(path):
                 lines = self.fs.get_content(path).splitlines(keepends=True)
                 
        return "".join(lines[:count]), "", 0

class TailCommand(TextOpCommand):
    async def execute(self, args, input_data=""):
        parser = argparse.ArgumentParser(prog="tail", add_help=False)
        parser.add_argument("-n", "--lines", type=int, default=10)
        parser.add_argument("files", nargs="*")
        
        try:
            parsed, unknown = parser.parse_known_args(args)
        except SystemExit:
            return "", "", 1
            
        count = parsed.lines
        files = parsed.files

        lines = []
        if not files:
             lines = input_data.splitlines(keepends=True)
        else:
             path = self.emulator.resolve_path(files[0])
             if self.fs.is_file(path):
                  lines = self.fs.get_content(path).splitlines(keepends=True)
                  
        return "".join(lines[-count:]), "", 0
