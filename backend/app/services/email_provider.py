"""
Email Provider Abstraction (Phase 2D-3A)

Provides a minimal email sending interface that can be implemented by different providers
(SMTP, SendGrid, AWS SES, etc.). The escalation service uses this abstraction
instead of directly calling SMTP.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import logging

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


# Global email provider instance (can be swapped for different environments)
_email_provider: Optional[EmailProvider] = None


def get_email_provider() -> EmailProvider:
    """Get the current email provider instance."""
    global _email_provider
    if _email_provider is None:
        # Default to mock provider for safety
        _email_provider = MockEmailProvider()
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