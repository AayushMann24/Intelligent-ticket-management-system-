"""
Email Provider Abstraction (Phase 2D-3A)

Provides a minimal email sending interface that can be implemented by different providers
(SMTP, SendGrid, AWS SES, etc.). The escalation service uses this abstraction
instead of directly calling SMTP.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import asyncio
import logging
import smtplib
from email.message import EmailMessage as _StdlibEmailMessage
from email.utils import formataddr, make_msgid

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message to be sent."""
    to: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None


@dataclass
class EmailResult:
    """Result of email sending attempt."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailProvider(ABC):
    """Abstract base class for email providers."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send an email message. Returns EmailResult with success status."""
        pass


class MockEmailProvider(EmailProvider):
    """
    Mock email provider for testing and development.
    Logs emails instead of actually sending them.
    """

    def __init__(self):
        self.sent_emails = []

    async def send(self, message: EmailMessage) -> EmailResult:
        logger.info(f"[MOCK EMAIL] To: {message.to}, Subject: {message.subject}")
        logger.debug(f"[MOCK EMAIL] Body: {message.body_text}")
        self.sent_emails.append(message)
        return EmailResult(success=True, message_id="mock-message-id")


class ConsoleEmailProvider(EmailProvider):
    """
    Console email provider that prints emails to stdout.
    Useful for development and debugging.
    """

    async def send(self, message: EmailMessage) -> EmailResult:
        print(f"\n{'='*60}")
        print(f"EMAIL SENT")
        print(f"To: {message.to}")
        print(f"Subject: {message.subject}")
        print(f"From: {message.from_name or 'ITMS'} <{message.from_email or 'noreply@itms.local'}>")
        print(f"Body:")
        print(f"{message.body_text}")
        print(f"{'='*60}\n")
        return EmailResult(success=True, message_id="console-message-id")


class SMTPEmailProvider(EmailProvider):
    """
    SMTP email provider.

    Sends real email through a configured SMTP server. This provider is only
    used when EMAIL_PROVIDER=smtp; the default remains the mock provider so
    that development and tests never send real email.

    Credentials are read from settings and are never logged or returned to
    callers. Delivery is only reported as successful when the SMTP server
    accepts the message.
    """

    def __init__(
        self,
        host: Optional[str],
        port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: int = 10,
        default_from_email: Optional[str] = None,
        default_from_name: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.default_from_email = default_from_email or "noreply@itms.local"
        self.default_from_name = default_from_name or "ITMS Notifications"

    def _build_message(self, message: EmailMessage) -> _StdlibEmailMessage:
        msg = _StdlibEmailMessage()
        from_email = message.from_email or self.default_from_email
        from_name = message.from_name or self.default_from_name

        msg["From"] = formataddr((from_name, from_email)) if from_name else from_email
        msg["To"] = message.to
        msg["Subject"] = message.subject
        msg["Message-ID"] = make_msgid()
        msg.set_content(message.body_text)
        if message.body_html:
            msg.add_alternative(message.body_html, subtype="html")
        return msg

    def _send_sync(self, message: EmailMessage) -> str:
        """Blocking SMTP send. Runs in a worker thread via asyncio.to_thread."""
        msg = self._build_message(message)

        if self.use_ssl:
            smtp = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
        else:
            smtp = smtplib.SMTP(self.host, self.port, timeout=self.timeout)

        try:
            if not self.use_ssl and self.use_tls:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            if self.username:
                smtp.login(self.username, self.password or "")
            smtp.send_message(msg)
        finally:
            try:
                smtp.quit()
            except Exception:
                # A failure to close the connection does not change delivery status.
                pass

        return msg["Message-ID"]

    async def send(self, message: EmailMessage) -> EmailResult:
        if not self.host:
            return EmailResult(
                success=False,
                error="SMTP provider is not configured (SMTP_HOST is missing)",
            )

        try:
            # Offload the blocking SMTP conversation to a worker thread so the
            # event loop is not blocked.
            message_id = await asyncio.to_thread(self._send_sync, message)
            return EmailResult(success=True, message_id=message_id)
        except Exception as e:
            # Log the error type only - never log credentials or secrets.
            logger.error(
                "SMTP delivery failed to %s: %s", self.host, type(e).__name__
            )
            return EmailResult(success=False, error=f"{type(e).__name__}: {e}")


# Global email provider instance (can be swapped for different environments)
_email_provider: Optional[EmailProvider] = None


def build_email_provider() -> EmailProvider:
    """
    Construct the email provider selected by configuration.

    EMAIL_PROVIDER controls the choice:
      - "smtp"    -> SMTPEmailProvider (real delivery)
      - "console" -> ConsoleEmailProvider (prints to stdout)
      - anything else / unset -> MockEmailProvider (safe default)
    """
    provider = (getattr(settings, "email_provider", None) or "mock").strip().lower()

    if provider == "smtp":
        return SMTPEmailProvider(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
            use_ssl=settings.smtp_use_ssl,
            timeout=settings.smtp_timeout_seconds,
            default_from_email=settings.email_from_address,
            default_from_name=settings.email_from_name,
        )

    if provider == "console":
        return ConsoleEmailProvider()

    return MockEmailProvider()


def get_email_provider() -> EmailProvider:
    """Get the current email provider instance."""
    global _email_provider
    if _email_provider is None:
        # Default to the configured provider; mock remains the safe default.
        _email_provider = build_email_provider()
    return _email_provider


def set_email_provider(provider: EmailProvider) -> None:
    """Set the email provider instance (for testing or configuration)."""
    global _email_provider
    _email_provider = provider


async def send_email(
    to: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> EmailResult:
    """
    Convenience function to send an email using the configured provider.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body_text: Plain text body
        body_html: Optional HTML body
        from_email: Optional sender email (uses default if not provided)
        from_name: Optional sender name (uses default if not provided)
        
    Returns:
        EmailResult with success status and any error message
    """
    provider = get_email_provider()
    message = EmailMessage(
        to=to,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        from_email=from_email,
        from_name=from_name,
    )
    return await provider.send(message)