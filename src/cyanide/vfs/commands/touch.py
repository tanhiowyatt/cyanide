from .base import Command


class TouchCommand(Command):
    async def execute(self, args, input_data=""):
        if not args:
            return "", "touch: missing file operand\n", 1

        for arg in args:
            # Ignore flags for now
            if arg.startswith("-"):
                continue

            path = self.emulator.resolve_path(arg)
            if self.fs.exists(path):
                # Update timestamp (fake)
                pass
            else:
                # Create empty file
                if self.fs.mkfile(path, content="", owner=self.username) is None:
                    return (
                        "",
                        f"touch: cannot touch '{arg}': No such file or directory\n",
                        1,
                    )

        return "", "", 0
