"""
Configuración de la conexión a la base de datos.

En producción se conecta a PostgreSQL mediante la variable de entorno
DATABASE_URL definida en docker-compose.yml. Para pruebas locales o
ejecución sin Docker cae automáticamente a SQLite, evitando que el
desarrollador requiera tener PostgreSQL instalado en su máquina.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tickets_local.db")

# Para SQLite, deshabilitar verificación de hilo único (Flask es multi-hilo).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Clase base declarativa de SQLAlchemy 2.x."""
    pass


def init_db() -> None:
    """Crea las tablas si no existen. Se llama una vez al iniciar la aplicación."""
    # Importación local para evitar dependencia circular con models.
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Elimina todas las tablas. Solo se usa en pruebas."""
    from app import models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
