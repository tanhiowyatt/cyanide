import asyncio

from .base import Command


class ChmodCommand(Command):
    async def execute(self, args, input_data=""):
        await asyncio.sleep(0)
        if len(args) < 2:
            return "", "chmod: missing operand\n", 1

        mode = args[0]
        targets = args[1:]

        for target in targets:
            path = self.emulator.resolve_path(target)
            node = self.fs.get_node(path)
            if not node:
                return (
                    "",
                    f"chmod: cannot access '{target}': No such file or directory\n",
                    1,
                )

            if mode.isdigit():
                current_perm = node.perm
                # Simple mapping for common octal modes
                mapping = {
                    "777": "rwxrwxrwx",
                    "755": "rwxr-xr-x",
                    "644": "rw-r--r--",
                    "600": "rw-------",
                }
                suffix = mapping.get(mode, current_perm[1:])
                prefix = "d" if node.is_dir() else "-"
                new_perm = prefix + suffix
                self.fs.chmod(path, new_perm)
            else:
                if "+x" in mode:
                    p = list(node.perm)
                    p[3] = "x"
                    p[6] = "x"
                    p[9] = "x"
                    self.fs.chmod(path, "".join(p))

        return "", "", 0
