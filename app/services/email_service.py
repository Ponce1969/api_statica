"""Servicio de correo electrónico de aplicación.

Responsable de la orquestación del envío de correos electrónicos utilizando un puerto EmailSender y plantillas HTML.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.domain.email_protocol import EmailSender
from app.domain.models.contact import Contact

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"


env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailService:
    """Servicio de correo electrónico de aplicación."""

    def __init__(self, sender: EmailSender) -> None:  # noqa: D401, ANN001
        self._sender = sender

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def send_user_confirmation(self, contact: Contact) -> None:
        subject = "Registro confirmado"
        html_body = self._render("user_confirmation.html", full_name=contact.full_name)
        await self._sender.send_email(to=contact.email, subject=subject, html_body=html_body)

    async def notify_admin(self, contact: Contact) -> None:
        subject = "Nuevo usuario registrado"
        html_body = self._render(
            "admin_notification.html",
            full_name=contact.full_name,
            email=contact.email,
            message=contact.message,
        )
        await self._sender.send_email(
            to=str(settings.FIRST_SUPERUSER),
            subject=subject,
            html_body=html_body,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _render(self, template_name: str, **context: str) -> str:  # noqa: D401, ANN001
        template = env.get_template(template_name)
        rendered_content: str = template.render(**context)
        return rendered_content

    async def send_registration_emails(self, contact: Contact) -> None:
        """Enviar ambas confirmaciones y notificación al admin concurrentemente."""
        await asyncio.gather(
            self.send_user_confirmation(contact),
            self.notify_admin(contact),
        )
