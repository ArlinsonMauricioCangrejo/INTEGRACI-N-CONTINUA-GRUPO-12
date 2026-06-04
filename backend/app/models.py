"""
Modelo del dominio: Ticket de soporte.

Se mapea a la tabla `tickets` de PostgreSQL mediante SQLAlchemy ORM.
Mantiene las mismas validaciones de prioridad y estado que la versión
anterior en memoria, de modo que las pruebas y los consumidores del
modelo no cambian su contrato.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped

from app.database import Base

VALID_PRIORITIES = {"baja", "media", "alta"}
VALID_STATUSES = {"abierto", "en_progreso", "cerrado"}


class Priority:
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class Status:
    ABIERTO = "abierto"
    EN_PROGRESO = "en_progreso"
    CERRADO = "cerrado"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    description = Column(String(500), default="")
    priority = Column(String(20), default=Priority.MEDIA, nullable=False)
    status = Column(String(20), default=Status.ABIERTO, nullable=False)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now, nullable=False)

    @classmethod
    def new(cls, title: str, description: str = "", priority: str = "media") -> "Ticket":
        priority = (priority or "media").lower()
        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Prioridad inválida '{priority}'. Use: {', '.join(sorted(VALID_PRIORITIES))}"
            )
        return cls(
            title=title.strip(),
            description=(description or "").strip(),
            priority=priority,
            status=Status.ABIERTO,
        )

    def apply_update(self, status=None, priority=None, description=None, title=None) -> None:
        if status is not None:
            status = status.lower()
            if status not in VALID_STATUSES:
                raise ValueError(
                    f"Estado inválido '{status}'. Use: {', '.join(sorted(VALID_STATUSES))}"
                )
            self.status = status
        if priority is not None:
            priority = priority.lower()
            if priority not in VALID_PRIORITIES:
                raise ValueError(
                    f"Prioridad inválida '{priority}'. Use: {', '.join(sorted(VALID_PRIORITIES))}"
                )
            self.priority = priority
        if description is not None:
            self.description = description.strip()
        if title is not None and title.strip():
            self.title = title.strip()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None,
        }
