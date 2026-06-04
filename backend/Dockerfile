FROM python:3.11-slim

# Variables de entorno para Python en contenedor
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /code

# Instalación de dependencias del sistema (psycopg2 requiere libpq)
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# Instalación de dependencias Python primero (mejor caché de capas)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia del código fuente
COPY app/ ./app/
COPY tests/ ./tests/

# Puerto expuesto por la API Flask
EXPOSE 5000

# Verificación de salud para que docker-compose espere a que el backend esté listo
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=2)" || exit 1

CMD ["python", "-m", "app.main"]
