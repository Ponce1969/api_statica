"""Implementación de un remitente de correos mediante SMTP.

Este componente pertenece a la capa de *infraestructura*, ya que se encarga del 
acceso a IO externo (específicamente, el envío real de correos electrónicos). 
Implementa el puerto ``EmailSender`` definido en la capa de *dominio* para poder 
ser inyectado en cualquier parte sin romper el principio de Inversión de Dependencias.
"""

from __future__ import annotations

import asyncio
import logging
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL
from typing import Final

from app.core.config import settings
from app.domain.email_protocol import EmailSender

# Configuración del logger
logger = logging.getLogger(__name__)


class SMTPEmailSender(EmailSender):
    """Implementación concreta de un remitente de correos mediante SMTP.

    Para mantener la compatibilidad con servicios *async* esta clase envuelve la 
    llamada SMTP bloqueante en ``asyncio.to_thread`` para que el bucle de eventos 
    principal no se bloquee.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        use_ssl: bool = False,
    ) -> None:
        # Manejo seguro de valores que podrían ser None
        self._host: Final[str] = host if host is not None else str(settings.SMTP_HOST or "")
        self._port: Final[int] = port if port is not None else (int(settings.SMTP_PORT) if settings.SMTP_PORT is not None else 25)
        self._username: Final[str] = username if username is not None else str(settings.SMTP_USERNAME or "")
        self._password: Final[str] = password if password is not None else str(settings.SMTP_PASSWORD or "")
        self._use_tls: Final[bool] = use_tls
        self._use_ssl: Final[bool] = use_ssl if use_ssl else bool(settings.SMTP_SSL)

    async def send_email(self, *, to: str, subject: str, html_body: str) -> None:  # noqa: D401, ANN001
        await asyncio.to_thread(self._send_sync, to=to, subject=subject, html_body=html_body)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _send_sync(self, *, to: str, subject: str, html_body: str) -> None:  # noqa: ANN001
        """Envío SMTP bloqueante; ejecutado en un hilo."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = str(settings.EMAILS_FROM_EMAIL)
        message["To"] = to
        message.attach(MIMEText(html_body, "html"))

        try:
            logger.info(f"Intentando conectar a {self._host}:{self._port} (SSL={self._use_ssl}, TLS={self._use_tls})")
            
            if self._use_ssl:
                # Modo SSL implícito (puerto 465)
                logger.info("Usando SSL implícito")
                context = ssl.create_default_context()
                with SMTP_SSL(self._host, self._port, context=context) as smtp:
                    smtp.set_debuglevel(1)
                    logger.info(f"Autenticando con usuario {self._username}")
                    smtp.login(self._username, self._password)
                    logger.info(f"Enviando email desde {settings.EMAILS_FROM_EMAIL} a {to}")
                    smtp.sendmail(str(settings.EMAILS_FROM_EMAIL), to, message.as_string())
                    logger.info("Email enviado correctamente")
            else:
                # Modo STARTTLS (puerto 587)
                logger.info("Usando SMTP con STARTTLS")
                with SMTP(self._host, self._port) as smtp:
                    smtp.set_debuglevel(1)
                    
                    if self._use_tls:
                        logger.info("Iniciando STARTTLS")
                        context = ssl.create_default_context()
                        smtp.starttls(context=context)
                    
                    logger.info(f"Autenticando con usuario {self._username}")
                    smtp.login(self._username, self._password)
                    
                    logger.info(f"Enviando email desde {settings.EMAILS_FROM_EMAIL} a {to}")
                    smtp.sendmail(str(settings.EMAILS_FROM_EMAIL), to, message.as_string())
                    logger.info("Email enviado correctamente")
            
        except Exception as exc:  # pragma: no cover – errores de red
            logger.error(f"Error enviando email: {type(exc).__name__}: {exc}")
            logger.exception("Detalles completos del error:")
            raise RuntimeError(f"Error enviando email: {type(exc).__name__}: {exc}") from exc
