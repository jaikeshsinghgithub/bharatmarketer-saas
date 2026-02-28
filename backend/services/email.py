import os
import logging
# import aioboto3  # Example for Amazon SES

logger = logging.getLogger(__name__)

EMAIL_FROM = os.getenv("EMAIL_FROM", "hello@bharatmarketer.in")

async def send_email(to_email: str, subject: str, html_body: str):
    """
    Mock service to send an email (to be replaced with SES, SendGrid, or SMTP)
    """
    logger.info(f"Mock Email -> {to_email}")
    logger.info(f"Subject: {subject}")
    # Here you would use aioboto3 for AWS SES or a SMTP client like aiosmtplib
    # For now, we mock the success.
    
    return {"status": "mocked", "to": to_email}
