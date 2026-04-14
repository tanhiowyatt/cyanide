from .base import Command


class DoasCommand(Command):
    async def execute(self, args, input_data=""):
        if not args:
            return (
                "",
                "usage: doas [-nSs] [-a style] [-C conf] [-u user] command [args]\n",
                1,
            )

        if self.emulator.username == "root":
            return await self._execute_subcommand(args, input_data)

        # Set up password prompt and internal callback that uses delegation
        self.emulator.pending_input_callback = lambda _: self._on_delegated_auth(
            args, input_data
        )
        self.emulator.pending_input_prompt = (
            f"[cyanide] password for {self.emulator.username}: "
        )
        return f"[cyanide] password for {self.emulator.username}: ", "", 0

    async def _on_delegated_auth(
        self, args: list[str], input_data: str
    ) -> tuple[str, str, int]:
        self.emulator.username = "root"
        return await self._execute_subcommand(args, input_data)
