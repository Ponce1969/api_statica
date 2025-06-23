"""Servicio de aplicaciones para `ContactRequest`."""
from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.config import settings
from app.domain.email_protocol import EmailSender
from app.domain.models.contact_request import ContactRequest
from app.domain.repositories.contact_request import IContactRequestRepository
from app.schemas.contact_request import ContactRequestCreate

# Importaciones jinja2 para las plantillas
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


class ContactRequestService:  # noqa: D101
    def __init__(
        self,
        *,
        repository: IContactRequestRepository,
        email_sender: EmailSender,
    ) -> None:
        self._repo = repository
        self._sender = email_sender

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def create_request(self, data: ContactRequestCreate) -> ContactRequest:
        """Crear la solicitud, almacenarla y enviar correos."""
        domain_obj = ContactRequest(
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            message=data.message,
        )
        await self._repo.create(domain_obj)
        await self._send_emails(domain_obj)
        return domain_obj

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def _send_emails(self, req: ContactRequest) -> None:
        admin_html = self._render(
            "contact_request_admin.html",
            full_name=req.full_name,
            email=req.email,
            phone=req.phone or "-",
            message=req.message,
        )
        user_html = self._render("contact_confirmation.html", full_name=req.full_name)

        await asyncio.gather(
            self._sender.send_email(
                to=str(settings.FIRST_SUPERUSER),
                subject="Nueva solicitud de contacto",
                html_body=admin_html,
            ),
            self._sender.send_email(
                to=req.email,
                subject="Hemos recibido tu solicitud",
                html_body=user_html,
            ),
        )

    def _render(self, template_name: str, **context: str) -> str:  # noqa: D401
        template = _env.get_template(template_name)
        rendered_content: str = str(template.render(**context))
        return rendered_content
