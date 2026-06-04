# Sistema de Gestión de Tickets de Soporte

Proyecto del Módulo **Énfasis Profesional I (Integración Continua)** del Politécnico Grancolombiano, Facultad de Ingeniería, Diseño e Innovación.

## Integrantes

- Carlos Mosquera Urrutia — Backend (API Flask, modelo de datos, pruebas)
- Vanessa Gómez Ruiz — Frontend (interfaz web, documentación, validación)
- Juan Peña Márquez — Base de Datos (PostgreSQL, esquema, persistencia)
- Arlinson Mauricio Cangrejo Díaz — DevOps / CI-CD (Docker, Jenkins, Travis CI, Codeship)

**Docente:** John Olarte

## Arquitectura

El sistema se compone de **tres contenedores Docker** comunicados entre sí mediante una red interna `ticket-net`:

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Frontend   │      │   Backend    │      │   Base de    │
│   (Nginx)   │─────▶│  (Flask API) │─────▶│    Datos     │
│  puerto 8080│      │  puerto 5000 │      │ (PostgreSQL) │
└─────────────┘      └──────────────┘      └──────────────┘
       ▲                     ▲                     ▲
       └─────────────────────┴─────────────────────┘
                       Red ticket-net
```

- **Frontend** (`ticket-frontend`): Nginx Alpine que sirve la interfaz web y enruta las peticiones `/api/*` al contenedor backend mediante proxy reverso.
- **Backend** (`ticket-backend`): API REST en Python 3.11 con Flask y SQLAlchemy. Se conecta a PostgreSQL por la variable de entorno `DATABASE_URL` resuelta a través del DNS interno de Docker (`db:5432`).
- **Base de Datos** (`ticket-db`): PostgreSQL 16 con volumen persistente `ticket-db-data` para conservar los tickets entre reinicios.

## Estructura del repositorio

```
ticket-system/
├── backend/                     ← Contenedor Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Rutas Flask (API REST)
│   │   ├── models.py            # Modelo Ticket (SQLAlchemy)
│   │   ├── storage.py           # Capa de almacenamiento
│   │   └── database.py          # Conexión y sesiones SQLAlchemy
│   └── tests/
│       └── test_api.py          # 13 pruebas pytest
├── frontend/                    ← Contenedor Frontend
│   ├── Dockerfile
│   ├── nginx.conf               # Proxy reverso /api/* → backend
│   └── html/
│       └── index.html           # Interfaz web
├── docker-compose.yml           ← Orquesta los 3 contenedores
├── .env.example
├── .gitignore
├── README.md
└── docs/
    └── architecture.md          # Notas técnicas
```

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows / macOS) o Docker Engine + Compose Plugin (Linux).
- Git.

No se necesita tener Python ni PostgreSQL instalados en la máquina: todo corre dentro de los contenedores.

## Levantar el proyecto

```bash
# Clonar el repositorio
git clone https://github.com/ArlinsonMauricioCangrejo/INTEGRACI-N-CONTINUA-GRUPO-12.git
cd INTEGRACI-N-CONTINUA-GRUPO-12

# Construir y levantar los tres contenedores
docker compose up --build
```

Tras unos segundos los tres contenedores estarán activos:

| Contenedor       | Puerto del host | URL                          |
|------------------|-----------------|------------------------------|
| ticket-frontend  | 8080            | http://localhost:8080        |
| ticket-backend   | 5000            | http://localhost:5000/api/health |
| ticket-db        | 5432            | postgresql://localhost:5432  |

Para detener:

```bash
docker compose down               # detiene y elimina los contenedores
docker compose down -v            # además elimina el volumen de datos
```

## Verificación de la comunicación entre contenedores

```bash
# Listar los contenedores corriendo
docker ps

# Ver la red interna y los contenedores conectados a ella
docker network inspect ticket-net

# Probar el endpoint de salud del backend desde fuera
curl http://localhost:5000/api/health

# Probar el proxy reverso del frontend hacia el backend
curl http://localhost:8080/api/health
```

## Ejecutar las pruebas

Las pruebas se pueden ejecutar de dos formas:

**Opción A — Dentro del contenedor backend (recomendado, igual que en CI):**

```bash
docker compose run --rm backend pytest -v
```

**Opción B — Localmente con SQLite (sin necesidad de levantar Docker):**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
pytest -v
```

## Endpoints del API

| Método | Ruta                       | Descripción                                  |
|--------|----------------------------|----------------------------------------------|
| GET    | `/api/health`              | Verificación de salud del servicio           |
| GET    | `/api/tickets`             | Listar todos los tickets                     |
| POST   | `/api/tickets`             | Crear un ticket                              |
| GET    | `/api/tickets/<id>`        | Consultar un ticket por su id                |
| PUT    | `/api/tickets/<id>`        | Actualizar título, descripción, prioridad o estado |
| DELETE | `/api/tickets/<id>`        | Eliminar un ticket                           |

### Ejemplos con curl

```bash
# Crear un ticket
curl -X POST http://localhost:8080/api/tickets \
  -H "Content-Type: application/json" \
  -d '{"title": "Servidor caído", "priority": "alta", "description": "Timeout SMTP"}'

# Listar tickets
curl http://localhost:8080/api/tickets

# Cambiar estado
curl -X PUT http://localhost:8080/api/tickets/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "en_progreso"}'
```

## Hoja de ruta del módulo

- **Semanas 1-2 (Foro):** estructura base del proyecto, repositorio en GitHub, MVP del backend.
- **Semana 3 (Entrega 1):** **arquitectura completa de tres contenedores Docker comunicados — estado actual.**
- **Semana 5 (Entrega 2):** Jenkins como orquestador del pipeline de CI.
- **Semanas 7-8 (Entrega 3 y sustentación):** Travis CI y Codeship + documentación final.
