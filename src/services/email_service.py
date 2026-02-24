import logging

from aiosmtplib import SMTP

from config.email_settings import EmailSettings
from src.email_templates.template_renderer import TemplateRenderer
from src.models.user import User

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, email_settings: EmailSettings, template_renderer: TemplateRenderer) -> None:
        self._settings = email_settings
        self._renderer = template_renderer

    async def _send_email(self, to_address: str, subject: str, html_body: str) -> None:
        if not self._settings.enabled:
            logger.info("Email disabled. Would send to %s: %s", to_address, subject)
            return

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self._settings.from_name} <{self._settings.from_address}>"
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            smtp = SMTP(hostname=self._settings.smtp_host, port=self._settings.smtp_port, use_tls=False)
            await smtp.connect()
            if self._settings.use_tls:
                await smtp.starttls()
            if self._settings.smtp_username:
                await smtp.login(self._settings.smtp_username, self._settings.smtp_password)
            await smtp.send_message(msg)
            await smtp.quit()
            logger.info("Email sent to %s: %s", to_address, subject)
        except Exception:
            logger.exception("Failed to send email to %s: %s", to_address, subject)

    async def send_match_request(self, initiator: User, target: User, token_uuid: str, base_url: str) -> None:
        html = self._renderer.render_match_request(
            initiator_name=initiator.full_name,
            initiator_branch=initiator.branch,
            target_name=target.full_name,
            approve_url=f"{base_url}/#/approve/{token_uuid}",
        )
        await self._send_email(
            to_address=target.email,
            subject=f"[האקתון] {initiator.full_name} רוצה להיות השותף/ה שלך",
            html_body=html,
        )

    async def send_match_approved(self, initiator: User, target: User) -> None:
        html = self._renderer.render_match_approved(
            initiator_name=initiator.full_name,
            target_name=target.full_name,
            target_branch=target.branch,
            target_email=target.email,
            target_phone=target.phone or "",
        )
        await self._send_email(
            to_address=initiator.email,
            subject=f"[האקתון] {target.full_name} אישר/ה את השותפות!",
            html_body=html,
        )

    async def send_match_rejected(self, initiator: User, target: User) -> None:
        html = self._renderer.render_match_rejected(
            initiator_name=initiator.full_name,
            target_name=target.full_name,
        )
        await self._send_email(
            to_address=initiator.email,
            subject=f"[האקתון] {target.full_name} דחה/תה את הבקשה",
            html_body=html,
        )

    async def send_match_cancelled(self, initiator: User, target: User) -> None:
        html = self._renderer.render_match_cancelled(
            initiator_name=initiator.full_name,
            target_name=target.full_name,
        )
        await self._send_email(
            to_address=target.email,
            subject=f"[האקתון] השותפות עם {initiator.full_name} בוטלה",
            html_body=html,
        )
