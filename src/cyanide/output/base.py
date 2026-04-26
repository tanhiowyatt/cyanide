import logging
import queue
import threading
import time
from abc import ABC
from typing import Any, Dict


class OutputPlugin(ABC):
    """
    Base class for all Cyanide output plugins.
    Implements a background thread with a thread-safe queue to ensure
    that slow network/database operations do not block the main honeypot emulator.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.queue: queue.Queue = queue.Queue(maxsize=10000)
        self.running = False
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.batch_size = self.config.get("batch_size", 1)
        self.batch_timeout = self.config.get("batch_timeout", 2.0)

    def start(self):
        """Start the background worker thread."""
        self.running = True
        self.worker_thread.start()

    def stop(self):
        """Stop the background worker thread and flush the queue."""
        self.running = False
        # We don't join here because it's a daemon thread,
        # but we wait a bit for it to finish processing.
        start_time = time.time()
        while not self.queue.empty() and time.time() - start_time < 5.0:
            time.sleep(0.1)
        self.close()

    def close(self):
        """Optional cleanup hook for subclasses."""
        pass

    def emit(self, event: Dict[str, Any]):
        """Enqueue an event for processing. Called by CyanideLogger."""
        if not self.running:
            return

        try:
            self.queue.put_nowait(event)
        except queue.Full:
            pass

    def _worker_loop(self):
        """Background thread loop to pull events and construct batches if necessary."""
        batch = []
        last_flush = time.time()

        while self.running or not self.queue.empty():
            try:
                # Use a small timeout to allow checking flush conditions
                event = self.queue.get(timeout=0.1)
                batch.append(event)
            except queue.Empty:
                pass

            if not batch:
                continue

            # Flush conditions:
            # 1. We reached batch size
            # 2. We reached timeout
            # 3. We are stopping and have items
            now = time.time()
            if (
                len(batch) >= self.batch_size
                or (now - last_flush) >= self.batch_timeout
                or (not self.running and self.queue.empty())
            ):
                try:
                    self.flush(batch)
                except Exception as e:
                    logging.error(f"[{self.__class__.__name__}] Flush error: {e}", exc_info=True)
                finally:
                    # Mark all items in batch as done
                    for _ in range(len(batch)):
                        self.queue.task_done()
                    batch = []
                    last_flush = now

    def flush(self, events: list[Dict[str, Any]]):
        """
        Process a batch of events.
        Default implementation calls write() for each event.
        Subclasses can override this for bulk operations (e.g. bulk SQL insert).
        """
        for event in events:
            try:
                self.write(event)
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] Write error: {e}", exc_info=True)

    def write(self, event: Dict[str, Any]):
        """
        Write a single event to the destination.
        Should be implemented by subclasses unless they override flush().
        """
        pass
