"""
Capa de almacenamiento del Sistema de Gestión de Tickets.

A partir de la Entrega 1 (Semana 3), el almacenamiento se realiza contra
PostgreSQL mediante SQLAlchemy ORM. La interfaz pública (add, get, all,
delete, update, clear) se conservó intacta respecto a la versión en
memoria de la Semana 1, de modo que las rutas Flask y las pruebas
automatizadas no requirieron cambios estructurales.
"""
from typing import List, Optional

from app.database import SessionLocal
from app.models import Ticket


class TicketStorage:
    """Encapsula el acceso a la base de datos. Cada operación maneja su propia sesión."""

    def add(self, ticket: Ticket) -> dict:
        session = SessionLocal()
        try:
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
            return ticket.to_dict()
        finally:
            session.close()

    def get(self, ticket_id: int) -> Optional[dict]:
        session = SessionLocal()
        try:
            ticket = session.get(Ticket, ticket_id)
            return ticket.to_dict() if ticket else None
        finally:
            session.close()

    def all(self) -> List[dict]:
        session = SessionLocal()
        try:
            tickets = session.query(Ticket).order_by(Ticket.id).all()
            return [t.to_dict() for t in tickets]
        finally:
            session.close()

    def update(self, ticket_id: int, **changes) -> Optional[dict]:
        """Aplica cambios al ticket dentro de una única transacción.

        Returns:
            dict con el ticket actualizado, o None si no existía.
        Raises:
            ValueError: cuando la prioridad o el estado son inválidos.
        """
        session = SessionLocal()
        try:
            ticket = session.get(Ticket, ticket_id)
            if ticket is None:
                return None
            ticket.apply_update(**changes)
            session.commit()
            session.refresh(ticket)
            return ticket.to_dict()
        finally:
            session.close()

    def delete(self, ticket_id: int) -> bool:
        session = SessionLocal()
        try:
            ticket = session.get(Ticket, ticket_id)
            if ticket is None:
                return False
            session.delete(ticket)
            session.commit()
            return True
        finally:
            session.close()

    def clear(self) -> None:
        """Vacía la tabla de tickets. Solo se usa en pruebas."""
        session = SessionLocal()
        try:
            session.query(Ticket).delete()
            session.commit()
        finally:
            session.close()
