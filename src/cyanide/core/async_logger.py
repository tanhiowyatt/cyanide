import asyncio
from pathlib import Path
from typing import Any, Union

import aiofiles


class AsyncLogger:
    """
    Asynchronous logger to perform file I/O in a background task.
    Prevents blocking the main event loop during high-volume logging (e.g., TTY recording).
    """

    # Function 9: Initializes the class instance and its attributes.
    def __init__(self):
        self.queue: "asyncio.Queue[Any]" = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self._worker_task = None

    # Function 10: Performs operations related to start.
    def start(self):
        """Start the background worker."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

    # Function 11: Performs operations related to stop.
    async def stop(self):
        """Stop the background worker and flush remaining logs."""
        self._stop_event.set()
        if self._worker_task:
            try:
                # Give it a few seconds to flush remaining logs
                await asyncio.wait_for(self.queue.join(), timeout=3.0)
            except asyncio.TimeoutError:
                pass

            # Cancel the worker if it's still running
            if not self._worker_task.done():
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass

    # Function 12: Handles event logging and telemetry.
    def log(self, filepath: Path, content: Union[str, bytes], mode: str = "a"):
        """Schedule a log write."""
        self.queue.put_nowait((filepath, content, mode))

    # Function 13: Performs operations related to worker.
    async def _worker(self):
        """Background task to process log queue."""
        while not self._stop_event.is_set() or not self.queue.empty():
            try:
                if self._stop_event.is_set():
                    try:
                        filepath, content, mode = self.queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                else:
                    item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                    filepath, content, mode = item

                try:
                    async with aiofiles.open(filepath, mode) as f:
                        await f.write(content)
                except Exception as e:
                    import sys

                    print(f"ERROR: AsyncLogger failed to write to {filepath}: {e}", file=sys.stderr)
                finally:
                    self.queue.task_done()

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                # Log to stderr since logging system might be closing
                import sys

                print("AsyncLogger worker cancelled, finishing queue...", file=sys.stderr)
                break
            except Exception as e:
                import sys

                print(f"AsyncLogger worker error: {e}", file=sys.stderr)
                await asyncio.sleep(0.1)  # Prevent tight loop on persistent error
                continue
