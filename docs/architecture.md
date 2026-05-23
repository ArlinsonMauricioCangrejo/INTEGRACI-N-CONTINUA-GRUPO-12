# Arquitectura del proyecto

## Visión general

El sistema se sustenta en una arquitectura de tres contenedores Docker comunicados entre sí mediante una red interna definida en `docker-compose.yml`:

1. **Contenedor Backend** — API REST en Python con Flask. Expone los endpoints documentados en el `README.md` y concentra la lógica de negocio.
2. **Contenedor Frontend** — Interfaz web que consume la API. En la Semana 1 está embebida dentro del propio backend (Flask + Jinja); en la Semana 3 se separa en un contenedor independiente sirviendo archivos estáticos.
3. **Contenedor Base de Datos** — PostgreSQL como motor de persistencia. Se incorpora en la Semana 3, reemplazando la implementación en memoria actual.

## Flujo de integración continua

```
Desarrolladores ──► Contenedores (Backend / Frontend / DB) ──► GitHub
                                                                  │
                                                                  ▼
                                                              Jenkins
                                                                  │
                                                                  ▼
                                                       Despliegue automatizado
```

Cada `push` o `pull request` dispara el pipeline de Jenkins, que:

1. Descarga el código del repositorio.
2. Construye las imágenes Docker.
3. Levanta los servicios con `docker-compose`.
4. Ejecuta las pruebas automatizadas con `pytest`.
5. Reporta el resultado al equipo y, si todo pasa, publica el build.

En las Semanas 7 y 8 se complementa con **Travis CI** y **Codeship** como servicios alojados, para comparar el modelo de servidor autogestionado (Jenkins) frente al de servicios en la nube.

## Decisiones técnicas

- **Flask sobre Django:** se eligió Flask por ser un microframework ligero y modular, adecuado al alcance acotado del módulo y a una arquitectura multi-contenedor. Django introduciría componentes (ORM, admin, middleware) innecesarios en este contexto.
- **PostgreSQL sobre SQLite:** PostgreSQL ofrece imagen Docker oficial mantenida, soporta concurrencia real y representa fielmente el escenario de producción de un sistema de tickets.
- **Almacenamiento en memoria en Semana 1:** permite avanzar con la estructura del proyecto y las pruebas automatizadas sin esperar a la incorporación de Docker en la Semana 3. La interfaz pública de `TicketStorage` se diseñó para que el reemplazo por PostgreSQL en Semana 3 no requiera cambios en `main.py`.
- **Pruebas con pytest:** sintaxis concisa, fixtures sencillas, integración nativa con Flask y soporte oficial en Jenkins, Travis CI y Codeship.

## Próximos pasos

| Semana | Entregable                                                                 |
|--------|----------------------------------------------------------------------------|
| 3      | `Dockerfile` del backend, `docker-compose.yml` con backend + frontend + DB |
| 5      | `Jenkinsfile` con stages de build, test y deploy                           |
| 7-8    | `.travis.yml`, archivo de Codeship, documento de cierre                    |
