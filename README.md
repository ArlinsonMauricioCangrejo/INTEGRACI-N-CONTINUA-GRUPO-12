# Sistema de Gestión de Tickets de Soporte

Proyecto del Módulo **Énfasis Profesional I (Integración Continua)** del Politécnico Grancolombiano, Facultad de Ingeniería, Diseño e Innovación.

## Integrantes

- Carlos Mosquera Urrutia
- Arlinson Mauricio Cangrejo Díaz

**Docente:** John Olarte

## Descripción

API REST y aplicación web para la gestión de tickets de soporte técnico. El sistema permite crear tickets con título, descripción y prioridad, asignarles un estado (abierto, en progreso, cerrado), consultarlos, actualizarlos y eliminarlos.

Este proyecto sirve de base para aplicar de forma incremental, durante las siete semanas del módulo, las herramientas de integración continua: GitHub, Docker, Jenkins, Travis CI y Codeship.

## Pila tecnológica

- **Lenguaje:** Python 3.10+
- **Framework web:** Flask
- **Pruebas:** pytest
- **Base de datos:** en memoria (Semana 1) → PostgreSQL contenerizado (Semana 3)
- **Orquestación:** Docker + docker-compose (Semana 3)
- **CI/CD:** Jenkins (Semana 5) + Travis CI y Codeship (Semana 7-8)

## Estructura del proyecto

```
ticket-system/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación Flask y rutas
│   ├── models.py            # Modelo Ticket y validaciones
│   ├── storage.py           # Capa de almacenamiento (en memoria)
│   └── templates/
│       └── index.html       # Interfaz web
├── tests/
│   ├── __init__.py
│   └── test_api.py          # Pruebas pytest del API
├── docs/
│   └── architecture.md      # Notas de arquitectura
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalación y ejecución

Se requiere **Python 3.10 o superior**.

```bash
# 1. Clonar el repositorio
git clone https://github.com/<usuario>/ticket-system.git
cd ticket-system

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python -m app.main
```

La aplicación queda disponible en `http://localhost:5000`.

## Ejecutar las pruebas

```bash
pytest -v
```

Las pruebas cubren los endpoints principales (health, crear, listar, consultar, actualizar y eliminar) y los casos de error (404, validaciones de prioridad y estado). En la Semana 5, Jenkins ejecutará automáticamente estas pruebas sobre cada cambio publicado en el repositorio.

## Endpoints del API

| Método | Ruta                       | Descripción                          |
|--------|----------------------------|--------------------------------------|
| GET    | `/`                        | Interfaz web                         |
| GET    | `/api/health`              | Verificación de salud del servicio   |
| GET    | `/api/tickets`             | Listar todos los tickets             |
| POST   | `/api/tickets`             | Crear un ticket                      |
| GET    | `/api/tickets/<id>`        | Consultar un ticket por su id        |
| PUT    | `/api/tickets/<id>`        | Actualizar título, descripción, prioridad o estado |
| DELETE | `/api/tickets/<id>`        | Eliminar un ticket                   |

### Ejemplo: crear un ticket

```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{"title": "Servidor de correo no responde", "priority": "alta", "description": "El servidor SMTP devuelve timeout desde las 8:00 AM"}'
```

### Ejemplo: cambiar estado de un ticket

```bash
curl -X PUT http://localhost:5000/api/tickets/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "en_progreso"}'
```

## Modelo de datos

Cada ticket tiene los siguientes campos:

| Campo         | Tipo    | Valores válidos                                |
|---------------|---------|------------------------------------------------|
| `id`          | int     | Auto-incrementado                              |
| `title`       | string  | Obligatorio, máx. 120 caracteres               |
| `description` | string  | Opcional, máx. 500 caracteres                  |
| `priority`    | string  | `baja`, `media`, `alta`                        |
| `status`      | string  | `abierto`, `en_progreso`, `cerrado`            |
| `created_at`  | string  | Fecha-hora ISO 8601 (UTC)                      |
| `updated_at`  | string  | Fecha-hora ISO 8601 (UTC)                      |

## Hoja de ruta del módulo

- **Semanas 1-2:** estructura base del proyecto, repositorio en GitHub, aplicación Flask funcional en memoria. *(Estado actual.)*
- **Semana 3 (Entrega 1):** contenerización con Docker. Tres contenedores comunicados: backend Flask, frontend web y base de datos PostgreSQL, orquestados con `docker-compose`.
- **Semana 5 (Entrega 2):** Jenkins como orquestador de operaciones, pipeline de construcción y prueba automatizada disparado por cada push.
- **Semanas 7-8 (Entrega 3 y sustentación):** integración con Travis CI y Codeship, consolidación documental y sustentación final.

## Convenciones de trabajo

- Ramas con prefijo: `feature/*`, `fix/*`, `docs/*`.
- Todo cambio sobre `main` debe pasar por **pull request** con revisión del otro integrante.
- Mensajes de commit en verbo infinitivo en español: `agregar endpoint de health`, `corregir validación de prioridad`, etc.
