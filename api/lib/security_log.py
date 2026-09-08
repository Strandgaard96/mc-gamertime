"""Structured security-event logging.

Emits one JSON object per event to the "security" logger. Fields are passed as
kwargs and serialized with json.dumps — which escapes newlines/control chars, so
user-controlled values (usernames, paths) can never forge extra log lines
(CWE-117 log injection). Never pass secrets (passwords, tokens) as fields.

No handler is configured here on purpose: on Lambda the AWS runtime attaches a
root handler (records propagate to CloudWatch); under uvicorn the default root
handler writes to stderr. Emitting is enough.
"""

from __future__ import annotations

import json
import logging

_log = logging.getLogger("security")


def log_security_event(event: str, **fields) -> None:
    _log.warning(json.dumps({"event": event, **fields}, default=str))
