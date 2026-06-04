# Arquitectura del proyecto — Entrega 1 (Semana 3)

## Visión general

El sistema se sustenta en una arquitectura de **tres contenedores Docker independientes y comunicados** entre sí mediante una red interna `ticket-net` definida en `docker-compose.yml`:

1. **Contenedor Frontend** (`ticket-frontend`) — Nginx 1.27 Alpine sirviendo la interfaz web. Actúa además como proxy reverso: las solicitudes que llegan a `/api/*` se enrutan al contenedor backend usando el nombre de servicio `backend` que resuelve la red interna de Docker.

2. **Contenedor Backend** (`ticket-backend`) — Python 3.11 con Flask y SQLAlchemy. Expone los endpoints REST y se conecta a PostgreSQL a través del nombre de servicio `db` (resuelto por DNS interno de Docker Compose) en el puerto 5432, autenticándose con las credenciales definidas en variables de entorno.

3. **Contenedor Base de Datos** (`ticket-db`) — PostgreSQL 16 Alpine con volumen persistente `ticket-db-data` montado en `/var/lib/postgresql/data` para conservar los tickets entre reinicios del contenedor.

## Comunicación entre contenedores

```
Usuario
   │
   ▼
┌──────────────────────────────────────────────────────────┐
│  ticket-frontend (Nginx, puerto 80 interno / 8080 host)  │
│                                                          │
│   ┌───────────────────────────────────────────┐          │
│   │ location / → /usr/share/nginx/html/       │          │
│   │ location /api/ → proxy_pass http://backend:5000 │    │
│   └───────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼ red interna ticket-net
┌──────────────────────────────────────────────────────────┐
│  ticket-backend (Flask, puerto 5000)                     │
│                                                          │
│   DATABASE_URL=postgresql://ticket_user:***@db:5432/...  │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼ red interna ticket-net
┌──────────────────────────────────────────────────────────┐
│  ticket-db (PostgreSQL 16, puerto 5432)                  │
│                                                          │
│   volumen ticket-db-data:/var/lib/postgresql/data        │
└──────────────────────────────────────────────────────────┘
```

Los nombres de host (`backend`, `db`) son resueltos automáticamente por el DNS interno de Docker Compose; los contenedores no se hablan por IP sino por nombre de servicio. Esto es lo que evidencia la **comunicación entre contenedores** que exige la guía del módulo.

## Aseguramiento del orden de arranque

PostgreSQL tarda algunos segundos en estar listo para aceptar conexiones. Para evitar que el backend intente conectarse antes de tiempo, se configuró:

1. Un **healthcheck** sobre el contenedor `db` que ejecuta `pg_isready` cada 5 segundos.
2. Una dependencia `depends_on: { db: { condition: service_healthy } }` en el servicio backend, que retrasa su arranque hasta que el contenedor de base de datos pase su healthcheck.

## Decisiones técnicas

| Tema                       | Decisión                                              | Justificación                                                                                       |
|----------------------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Framework backend          | Flask                                                 | Microframework ligero, ajustado al alcance del módulo y a una arquitectura multi-contenedor.        |
| ORM                        | SQLAlchemy 2.x                                        | Permite portabilidad entre SQLite (pruebas) y PostgreSQL (producción) sin cambiar código.           |
| Motor de base de datos     | PostgreSQL 16 Alpine                                  | Imagen oficial mantenida, soporte de transacciones, representa el escenario real de producción.    |
| Servidor frontend          | Nginx 1.27 Alpine                                     | Ligero, configuración simple para proxy reverso, imagen oficial.                                    |
| Comunicación entre contenedores | Red bridge `ticket-net` con DNS interno          | Aislamiento del host, los servicios se descubren por nombre, no por IP.                             |
| Persistencia               | Volumen Docker `ticket-db-data`                       | Los datos sobreviven a reinicios y reconstrucciones de contenedores.                                |
| Variables sensibles        | Archivo `.env` ignorado por Git, `.env.example` versionado | Las credenciales no quedan en el repositorio público.                                          |

## Próximos pasos (Entregas 2 y 3)

| Semana | Entregable                                                                       |
|--------|----------------------------------------------------------------------------------|
| 5      | `Jenkinsfile` con etapas de build, test y deploy. Contenedor Jenkins añadido al stack. |
| 7-8    | `.travis.yml`, integración con Codeship, documento de cierre y sustentación.     |
