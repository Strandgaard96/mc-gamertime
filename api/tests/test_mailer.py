import smtplib

from lib.mailer import send_email


def test_send_email_no_smtp_host_logs_instead_on_selfhost(monkeypatch, capsys):
    # Selfhost (SECRETS_PROVIDER=env): no mail server → print the message so the
    # operator can read the reset link from local docker logs.
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.setenv("SECRETS_PROVIDER", "env")
    send_email(to="alice@example.com", subject="Subject", body="Body text")
    captured = capsys.readouterr()
    assert "alice@example.com" in captured.out
    assert "Subject" in captured.out


def test_send_email_no_smtp_host_does_not_print_body_on_cloud(monkeypatch, capsys):
    # L-1: on cloud (SECRETS_PROVIDER=ssm) a missing SMTP_HOST must NOT print the
    # body — it may contain a live reset token that would land in CloudWatch.
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.setenv("SECRETS_PROVIDER", "ssm")
    send_email(to="alice@example.com", subject="Subject", body="Body text with token")
    captured = capsys.readouterr()
    assert "token" not in captured.out
    assert "alice@example.com" not in captured.out


def test_send_email_sends_via_smtp_when_configured(monkeypatch, mocker):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "bot")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM_ADDRESS", "noreply@example.com")

    mock_server = mocker.MagicMock()
    mock_smtp_cls = mocker.patch("lib.mailer.smtplib.SMTP")
    mock_smtp_cls.return_value.__enter__.return_value = mock_server

    send_email(to="alice@example.com", subject="Reset", body="Click here")

    mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("bot", "secret")
    mock_server.send_message.assert_called_once()
    sent_msg = mock_server.send_message.call_args[0][0]
    assert sent_msg["To"] == "alice@example.com"
    assert sent_msg["From"] == "noreply@example.com"
    assert sent_msg["Subject"] == "Reset"


def test_send_email_skips_login_without_credentials(monkeypatch, mocker):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)

    mock_server = mocker.MagicMock()
    mock_smtp_cls = mocker.patch("lib.mailer.smtplib.SMTP")
    mock_smtp_cls.return_value.__enter__.return_value = mock_server

    send_email(to="alice@example.com", subject="Reset", body="Click here")

    mock_server.login.assert_not_called()
    mock_server.send_message.assert_called_once()


# Quiet the unused-import lint until Step 3 adds the real smtplib usage path.
_ = smtplib
