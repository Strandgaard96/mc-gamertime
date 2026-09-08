"""Stdlib SMTP mailer for selfhost password reset (no new dependency).

SMTP_HOST unset (the default) -> send_email() logs the message instead of
sending it, so selfhosters without a mail server can still see reset links
via `docker compose logs mc-gamertime`.
"""

from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

log = logging.getLogger("mailer")


def _is_selfhost() -> bool:
    # Selfhost default; the cloud path sets SECRETS_PROVIDER=ssm explicitly.
    return os.environ.get("SECRETS_PROVIDER", "env") == "env"


def send_email(*, to: str, subject: str, body: str) -> None:
    host = os.environ.get("SMTP_HOST", "")
    if not host:
        if _is_selfhost():
            # Documented selfhost convenience: no mail server → print the message
            # (incl. the reset link) so the operator can read it from local
            # `docker compose logs`. Only safe because those logs are operator-only.
            print(f"[mailer] SMTP_HOST not set — would send to {to}\nSubject: {subject}\n{body}")  # noqa: T201
        else:
            # Cloud: NEVER write the body to CloudWatch — it may contain a live
            # password-reset token (CWE-532). Log a non-sensitive marker only.
            log.error("SMTP_HOST not configured; email not sent (subject=%s)", subject)
        return

    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ.get("SMTP_USERNAME", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    from_addr = os.environ.get("SMTP_FROM_ADDRESS", username or "noreply@localhost")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to
    msg.set_content(body)

    # Verified TLS: create_default_context() checks the server cert and raises if
    # STARTTLS is unavailable, so the message is never sent over cleartext (CWE-319).
    with smtplib.SMTP(host, port, timeout=10) as server:
        server.starttls(context=ssl.create_default_context())
        if username and password:
            server.login(username, password)
        server.send_message(msg)
