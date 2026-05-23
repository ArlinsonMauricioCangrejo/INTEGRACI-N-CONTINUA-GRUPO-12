"""
Capa de almacenamiento del Sistema de Gestión de Tickets.

Implementación en memoria para la Semana 1. En la Semana 3, cuando se
incorpore el contenedor de PostgreSQL, esta clase se reemplaza por una
implementación con SQLAlchemy manteniendo la misma interfaz pública
(add / get / all / delete), de modo que el resto de la aplicación no
requiere cambios.
"""
from threading import Lock
from typing import Dict, List, Optional

from app.models import Ticket


class TicketStorage:
    def __init__(self) -> None:
        self._items: Dict[int, Ticket] = {}
        self._next_id: int = 1
        self._lock: Lock = Lock()

    def add(self, ticket: Ticket) -> Ticket:
        with self._lock:
            ticket.id = self._next_id
            self._items[ticket.id] = ticket
            self._next_id += 1
            return ticket

    def get(self, ticket_id: int) -> Optional[Ticket]:
        return self._items.get(ticket_id)

    def all(self) -> List[Ticket]:
        return sorted(self._items.values(), key=lambda t: t.id)

    def delete(self, ticket_id: int) -> bool:
        with self._lock:
            return self._items.pop(ticket_id, None) is not None

    def clear(self) -> None:
        """Solo para uso en pruebas."""
        with self._lock:
            self._items.clear()
            self._next_id = 1
