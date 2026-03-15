import smtplib
from email.message import EmailMessage
from pavouci_api.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
import logging

logger = logging.getLogger(__name__)

def send_verification_email(to_email: str, subject: str, body: str):
    """Send verification email via SMTP if configured. If not configured, log the body.

    Returns True if email sent, False if not sent (logged).
    """
    if not SMTP_HOST or not FROM_EMAIL:
        logger.info("SMTP not configured; verification email:\n%s", body)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        port = SMTP_PORT or 587
        with smtplib.SMTP(SMTP_HOST, port) as smtp:
            smtp.starttls()
            if SMTP_USER and SMTP_PASS:
                smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send verification email: %s", e)
        return False
