import asyncio

from .base import Command


class PerlCommand(Command):
    async def execute(self, args, input_data=""):
        await asyncio.sleep(0.1)

        # Log all perl execution attempts
        if self.emulator.logger:
            self.emulator.logger.log_event(
                self.emulator.session_id,
                "perl_execution_attempt",
                {"args": args, "input_len": len(input_data)},
            )

        if "-v" in args:
            return (
                "This is perl 5, version 34, subversion 0 (v5.34.0) built for x86_64-linux-gnu-thread-multi\n",
                "",
                0,
            )

        # Handle perl -e "..."
        if "-e" in args:
            try:
                e_idx = args.index("-e")
                if e_idx + 1 < len(args):
                    script = args[e_idx + 1]
                    if self.emulator.logger:
                        self.emulator.logger.log_event(
                            self.emulator.session_id,
                            "perl_script_payload",
                            {"script": script},
                        )
                    # Imitate silent successful execution
                    return "", "", 0
            except (ValueError, IndexError):
                pass

        if len(args) > 0 and not args[0].startswith("-"):
            target = self.emulator.resolve_path(args[0])
            if not self.fs.exists(target):
                return (
                    "",
                    f'Can\'t open perl script "{args[0]}": No such file or directory\n',
                    2,
                )

            if self.emulator.logger:
                content = self.fs.get_content(target)
                if isinstance(content, bytes):
                    content = content.decode("utf-8", "ignore")
                self.emulator.logger.log_event(
                    self.emulator.session_id,
                    "perl_file_run",
                    {"file": args[0], "content": content},
                )
            return "", "", 0

        # Perl usually reads from stdin if no args. For honeypot, we'll just be silent or return nothing.
        return "", "", 0
