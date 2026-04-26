import json
import logging
from typing import Any, Dict

import requests

from .base import OutputPlugin


class Plugin(OutputPlugin):
    """
    Telegram Bot Output Plugin.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get("token", "")
        self.chat_id = config.get("chat_id", "")
        self.max_length = config.get("max_content_length", 4096)

    def flush(self, events: list[Dict[str, Any]]):
        if not self.token or not self.chat_id or not events:
            return

        messages = []
        current_message = ""

        for event in events:
            session = event.get("session", "unknown")
            eventid = event.get("eventid", "unknown")
            data = {k: v for k, v in event.items() if k not in ["timestamp", "session", "eventid"]}

            event_text = (
                f"<b>Cyanide Event</b>: <code>{eventid}</code>\n"
                f"<b>Session</b>: <code>{session}</code>\n"
                f"<b>Details</b>:\n<pre>{json.dumps(data, indent=2)}</pre>\n"
            )

            # If a single event is too long, truncate the JSON part
            if len(event_text) > self.max_length:
                # Basic truncation, might break HTML if not careful but <pre> is relatively safe
                truncated_data = json.dumps(data, indent=2)[: self.max_length - 300]
                event_text = (
                    f"<b>Cyanide Event</b>: <code>{eventid}</code>\n"
                    f"<b>Session</b>: <code>{session}</code>\n"
                    f"<b>Details (Truncated)</b>:\n<pre>{truncated_data}...</pre>\n"
                )

            if len(current_message) + len(event_text) > self.max_length:
                if current_message:
                    messages.append(current_message)
                current_message = event_text
            else:
                current_message += event_text

        if current_message:
            messages.append(current_message)

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        for msg in messages:
            payload = {
                "chat_id": self.chat_id,
                "text": msg,
                "parse_mode": "HTML",
            }

            try:
                resp = requests.post(url, json=payload, timeout=5)
                if resp.status_code != 200:
                    logging.error(
                        f"[Telegram] Write error: status={resp.status_code} text={resp.text}"
                    )
            except Exception as e:
                logging.error(f"[Telegram] Delivery failure: {e}")

    def write(self, event: Dict[str, Any]):
        self.flush([event])
