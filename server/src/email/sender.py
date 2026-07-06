import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.config import settings

logger = logging.getLogger(__name__)

try:
    import aiosmtplib

    HAS_AIOSMTP = True
except ImportError:
    HAS_AIOSMTP = False


class EmailSender:
    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    async def send(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        if not self.host or not self.username:
            logger.warning("SMTP not configured. Skipping email to %s", to_email)
            return False

        if not HAS_AIOSMTP:
            logger.warning("aiosmtplib not installed. Skipping email to %s", to_email)
            return False

        message = MIMEMultipart("alternative")
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        message["Subject"] = subject

        if text_body:
            message.attach(MIMEText(text_body, "plain"))

        message.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True,
            )
            logger.info("Email sent to %s", to_email)
            return True
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to_email, exc)
            return False


sender = EmailSender()
