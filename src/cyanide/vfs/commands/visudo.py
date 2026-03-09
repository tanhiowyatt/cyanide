from .base import Command


class VisudoCommand(Command):
    # Function 274: Executes the 'visudo' command logic within the virtual filesystem.
    async def execute(self, args, input_data=""):
        if self.emulator.username != "root":
            return (
                "",
                "visudo: /etc/sudoers: Permission denied\nvisudo: /etc/sudoers: Permission denied\n",
                1,
            )
        return "visudo: /etc/sudoers: success\n", "", 0
