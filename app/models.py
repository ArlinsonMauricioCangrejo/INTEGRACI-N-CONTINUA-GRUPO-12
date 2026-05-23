"""
Modelo del dominio: Ticket de soporte.

En la Semana 3 esta clase se reemplaza por un modelo SQLAlchemy mapeado
contra PostgreSQL. Por ahora usa dataclasses para mantener simple la base
y permitir que el equipo se concentre en la arquitectura del proyecto y
en la integración continua.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

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


@dataclass
class Ticket:
    id: int
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    updated_at: str

    @classmethod
    def new(cls, title: str, description: str = "", priority: str = "media") -> "Ticket":
        priority = (priority or "media").lower()
        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Prioridad inválida '{priority}'. Use: {', '.join(sorted(VALID_PRIORITIES))}"
            )
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            id=0,  # asignado por el almacenamiento
            title=title.strip(),
            description=(description or "").strip(),
            priority=priority,
            status=Status.ABIERTO,
            created_at=now,
            updated_at=now,
        )

    def update(self, status=None, priority=None, description=None, title=None):
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
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
