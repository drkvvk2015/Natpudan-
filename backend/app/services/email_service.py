"""Email service utilities for transactional notifications."""

import logging
import os
import smtplib
from email.message import EmailMessage
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Minimal SMTP-based email sender for security-sensitive notifications."""

    def __init__(self) -> None:
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "no-reply@natpudan.local")

    def is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_username and self.smtp_password)

    def send_password_reset_email(self, to_email: str, reset_link: str, full_name: Optional[str] = None) -> bool:
        """Send password reset link email. Returns True when delivered."""
        subject = "Natpudan Password Reset Request"
        greeting_name = full_name or "User"

        body = (
            f"Hello {greeting_name},\n\n"
            "We received a request to reset your password for your Natpudan account.\n\n"
            f"Reset your password using this secure link:\n{reset_link}\n\n"
            "This link expires in 1 hour. If you did not request this reset, you can safely ignore this email.\n\n"
            "Regards,\nNatpudan Security"
        )

        return self._send_email(to_email=to_email, subject=subject, body=body)

    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        if not self.is_configured():
            logger.warning("SMTP not configured. Skipping email send to %s", to_email)
            return False

        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            message.set_content(body)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as smtp:
                if self.smtp_use_tls:
                    smtp.starttls()
                smtp.login(self.smtp_username, self.smtp_password)
                smtp.send_message(message)

            logger.info("Password reset email sent to %s", to_email)
            return True
        except Exception as exc:
            logger.error("Failed sending email to %s: %s", to_email, exc, exc_info=True)
            return False


_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
