import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config.settings import settings


def _send_via_tls(to_email: str, msg: MIMEMultipart) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
        if settings.email_debug:
            server.set_debuglevel(1)
        if settings.smtp_use_tls:
            server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.sender_email, [to_email], msg.as_string())


def _send_via_ssl(to_email: str, msg: MIMEMultipart) -> None:
    with smtplib.SMTP_SSL(settings.smtp_host, 465, timeout=20) as server:
        if settings.email_debug:
            server.set_debuglevel(1)
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.sender_email, [to_email], msg.as_string())


def send_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None):
    if not all([settings.smtp_host, settings.smtp_port, settings.smtp_user, settings.smtp_password, settings.sender_email]):
        raise RuntimeError("SMTP no configurado. Define SMTP en .env")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.sender_email
    msg["To"] = to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        _send_via_tls(to_email, msg)
    except (smtplib.SMTPException, Exception) as e_tls:
        # Fallback a SSL 465 si falla TLS
        try:
            _send_via_ssl(to_email, msg)
        except (smtplib.SMTPException, Exception) as e_ssl:
            if isinstance(e_tls, smtplib.SMTPAuthenticationError):
                raise RuntimeError(f"SMTPAuthenticationError(TLS): {e_tls}")
            if isinstance(e_tls, smtplib.SMTPConnectError):
                raise RuntimeError(f"SMTPConnectError(TLS): {e_tls}")
            raise RuntimeError(f"SMTP error TLS: {e_tls} | SSL: {e_ssl}")
