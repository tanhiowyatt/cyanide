import json
import logging
from typing import Any, Dict

import requests

from .base import OutputPlugin


class Plugin(OutputPlugin):
    """
    Discord Webhook Output Plugin.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")
        self.username = config.get("username", "Cyanide Honeypot")
        self.max_length = config.get("max_content_length", 2000)

    def flush(self, events: list[Dict[str, Any]]):
        if not self.webhook_url or not events:
            return

        messages = []
        current_message = ""

        for event in events:
            session = event.get("session", "unknown")
            eventid = event.get("eventid", "unknown")
            data = {k: v for k, v in event.items() if k not in ["timestamp", "session", "eventid"]}

            event_text = (
                f"**{self.username} Event**: `{eventid}`\n"
                f"**Session**: `{session}`\n"
                f"**Details**: ```json\n{json.dumps(data, indent=2)}\n```\n"
            )

            # If a single event is too long, truncate the JSON part
            if len(event_text) > self.max_length:
                truncated_data = json.dumps(data, indent=2)[: self.max_length - 200]
                event_text = (
                    f"**{self.username} Event**: `{eventid}`\n"
                    f"**Session**: `{session}`\n"
                    f"**Details (Truncated)**: ```json\n{truncated_data}...\n```\n"
                )

            if len(current_message) + len(event_text) > self.max_length:
                if current_message:
                    messages.append(current_message)
                current_message = event_text
            else:
                current_message += event_text

        if current_message:
            messages.append(current_message)

        for msg in messages:
            payload = {
                "username": self.username,
                "content": msg,
            }

            try:
                resp = requests.post(self.webhook_url, json=payload, timeout=5)
                if resp.status_code not in [200, 204]:
                    logging.error(
                        f"[Discord] Write error: status={resp.status_code} text={resp.text}"
                    )
            except Exception as e:
                logging.error(f"[Discord] Delivery failure: {e}")

    def write(self, event: Dict[str, Any]):
        self.flush([event])
