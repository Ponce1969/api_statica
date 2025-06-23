"""Protocolo de correo electrónico (puerto).

Define el contrato que cualquier implementación de remitente de correo electrónico debe cumplir.  
Siguiendo Clean Architecture, la capa *dominio* posee los puertos y no depende de la infraestructura concreta.
"""

from typing import Protocol


class EmailSender(Protocol):
    """Abstracción para un remitente de correo electrónico asíncrono."""

    async def send_email(self, *, to: str, subject: str, html_body: str) -> None:  # noqa: D401, ANN001
        """Enviar un correo electrónico HTML.

        Args:
            to: Dirección de correo electrónico del destinatario.
            subject: Asunto del correo electrónico.
            html_body: Cuerpo HTML completo del correo electrónico.
        """
        raise NotImplementedError
