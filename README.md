# Sistema de Gestión de Tickets de Soporte

Proyecto del Módulo **Énfasis Profesional I (Integración Continua)** del Politécnico Grancolombiano, Facultad de Ingeniería, Diseño e Innovación.

## Integrantes

- Arlinson Mauricio Cangrejo Díaz — DevOps / CI-CD, Infraestructura y Frontend (Docker, Jenkins, Travis CI, CloudBees, Nginx, documentación)
- Carlos Mosquera Urrutia — Backend y Base de Datos (API Flask, modelo de datos, SQLAlchemy, PostgreSQL, pruebas pytest)

> Nota: el grupo se conformó originalmente con cuatro integrantes; el proyecto fue culminado por los dos integrantes listados, quienes asumieron de forma conjunta todas las áreas técnicas.

**Docente:** John Olarte

---

## Arquitectura

El sistema se compone de **tres contenedores Docker** comunicados entre sí mediante una red interna `ticket-net`, más un **cuarto contenedor opcional** (`ticket-jenkins`) que se activa para el pipeline de Integración Continua a partir de la Entrega 2.

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Frontend   │      │   Backend    │      │   Base de    │
│   (Nginx)   │─────▶│  (Flask API) │─────▶│    Datos     │
│  puerto 8080│      │  puerto 5000 │      │ (PostgreSQL) │
└─────────────┘      └──────────────┘      └──────────────┘
       ▲                     ▲                     ▲
       └─────────────────────┴─────────────────────┘
                       Red ticket-net
                              ▲
                              │
                     ┌────────┴────────┐
                     │     Jenkins     │
                     │  (CI/CD orq.)   │
                     │  puerto 8081    │
                     └─────────────────┘
```

- **Frontend** (`ticket-frontend`): Nginx Alpine que sirve la interfaz web y enruta las peticiones `/api/*` al contenedor backend mediante proxy reverso.
- **Backend** (`ticket-backend`): API REST en Python 3.11 con Flask y SQLAlchemy. Se conecta a PostgreSQL por la variable de entorno `DATABASE_URL` resuelta a través del DNS interno de Docker (`db:5432`).
- **Base de Datos** (`ticket-db`): PostgreSQL 16 con volumen persistente `ticket-db-data` para conservar los tickets entre reinicios.
- **Jenkins** (`ticket-jenkins`): orquestador del pipeline CI/CD. Construye, prueba y **despliega** el stack en cada cambio publicado en GitHub.

---

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
├── docker-compose.yml           ← Orquesta los 4 contenedores
├── Jenkinsfile                  ← Pipeline declarativo de CI/CD (Jenkins)
├── .travis.yml                  ← Pipeline de Travis CI (Entrega 3)
├── .env.example
├── .gitignore
├── README.md
└── docs/
    └── architecture.md          # Notas técnicas
```

---

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows / macOS) o Docker Engine + Compose Plugin (Linux).
- Git.
- Para la Entrega 2 (Jenkins): [ngrok](https://ngrok.com) con cuenta gratuita (solo para exponer Jenkins a GitHub durante el desarrollo).
- Para la Entrega 3 (Travis CI): cuenta en [travis-ci.com](https://app.travis-ci.com) y acceso al plan educativo vía [GitHub Student Developer Pack](https://education.github.com/pack).

No se necesita tener Python, Java ni PostgreSQL instalados en la máquina: todo corre dentro de los contenedores.

---

# Entrega 1 — Contenedores Docker (Semana 3)

## Levantar el proyecto

```bash
# Clonar el repositorio
git clone https://github.com/ArlinsonMauricioCangrejo/INTEGRACI-N-CONTINUA-GRUPO-12.git
cd INTEGRACI-N-CONTINUA-GRUPO-12

# Construir y levantar los tres contenedores principales del proyecto
docker compose up --build db backend frontend
```

> Nota: el comando `docker compose up --build` sin argumentos también levanta el contenedor de Jenkins. Si solo te interesa la Entrega 1, especificá los tres servicios como en el ejemplo.

Tras unos segundos los tres contenedores estarán activos:

| Contenedor       | Puerto del host | URL                              |
|------------------|-----------------|----------------------------------|
| ticket-frontend  | 8080            | http://localhost:8080            |
| ticket-backend   | 5000            | http://localhost:5000/api/health |
| ticket-db        | 5432            | postgresql://localhost:5432      |

Para detener:

```bash
docker compose down               # detiene y elimina los contenedores
docker compose down -v            # además elimina los volúmenes de datos
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
  -d '{"title": "Servidor caido", "priority": "alta", "description": "Timeout SMTP"}'

# Listar tickets
curl http://localhost:8080/api/tickets

# Cambiar estado
curl -X PUT http://localhost:8080/api/tickets/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "en_progreso"}'
```

---

# Entrega 2 — Pipeline CI/CD con Jenkins (Semana 5)

Esta sección documenta paso a paso cómo levantar el contenedor de Jenkins, configurarlo, integrarlo con GitHub y ejecutar el pipeline declarativo definido en el `Jenkinsfile`. Los pasos están pensados para ser reproducibles desde cero en cualquier máquina con Docker Desktop.

## Pre-requisitos

- Haber completado la Entrega 1 (el stack de tres contenedores debe poder levantarse).
- Cuenta en [GitHub](https://github.com) con permisos sobre el repositorio del proyecto.
- Cuenta gratuita en [ngrok](https://dashboard.ngrok.com/signup) — necesaria para exponer Jenkins a GitHub durante el desarrollo.

## Paso 1 — Levantar el contenedor de Jenkins

El servicio `jenkins` ya está definido en el `docker-compose.yml` del proyecto. Para levantarlo:

```bash
docker compose up -d jenkins
```

La primera vez la imagen `jenkins/jenkins:lts` se descarga (~500 MB), por lo que puede tardar varios minutos.

Verificar que está corriendo:

```bash
docker ps --filter "name=ticket-jenkins"
```

## Paso 2 — Configuración inicial de Jenkins

**2.1.** Obtener la contraseña inicial de administrador:

```bash
docker exec ticket-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copiarla a un editor de texto temporal.

**2.2.** Abrir en el navegador: <http://localhost:8081>

**2.3.** Pegar la contraseña en la pantalla *"Unlock Jenkins"* y dar clic en **Continue**.

**2.4.** Seleccionar **"Install suggested plugins"**. La instalación tarda entre 2 y 5 minutos.

**2.5.** Crear el usuario administrador en el formulario *"Create First Admin User"* (usuario, contraseña, nombre y correo).

**2.6.** Dejar la URL por defecto (`http://localhost:8081/`) en *"Instance Configuration"* y dar clic en **Save and Finish**.

**2.7.** Aterrizar en el dashboard principal de Jenkins.

## Paso 3 — Habilitar Docker dentro del contenedor Jenkins

La imagen oficial de Jenkins no incluye el CLI de Docker, por lo que es necesario instalarlo manualmente para que el pipeline pueda construir imágenes:

```bash
# Entrar al contenedor como root
docker exec -u root -it ticket-jenkins bash

# Dentro del contenedor:
apt-get update
apt-get install -y docker.io curl

# Instalar el plugin docker compose v2
mkdir -p /usr/local/lib/docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Instalar buildx (requerido por docker compose v2 para build)
curl -SL https://github.com/docker/buildx/releases/download/v0.20.0/buildx-v0.20.0.linux-amd64 \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx

# Dar permisos al socket de Docker del host
chmod 666 /var/run/docker.sock

# Verificar instalación
docker --version
docker compose version
docker buildx version

# Salir del contenedor
exit
```

> Nota: estos paquetes se pierden si se recrea el contenedor (`docker compose down` + `up`). Mientras solo se reinicie (`docker restart ticket-jenkins`) se mantienen.

## Paso 4 — Generar el Personal Access Token en GitHub

**4.1.** Acceder a <https://github.com/settings/tokens>

**4.2.** Clic en **Generate new token → Generate new token (classic)**.

**4.3.** Configurar:

| Campo      | Valor                          |
|------------|--------------------------------|
| Note       | `Jenkins Grupo 12`             |
| Expiration | `90 days`                      |
| Scopes     | `repo` y `admin:repo_hook` (marcar ambas casillas) |

**4.4.** Clic en **Generate token** y copiar el token (`ghp_...`) a un archivo temporal. El token se muestra una sola vez.

## Paso 5 — Configurar credenciales de GitHub en Jenkins

**5.1.** En Jenkins ir a **Administrar Jenkins → Credentials → System → (global) → + Add Credentials**.

**5.2.** Seleccionar **Username with password** y dar clic en **Next**.

**5.3.** Completar:

| Campo       | Valor                                                |
|-------------|------------------------------------------------------|
| Username    | `ArlinsonMauricioCangrejo` *(usuario de GitHub)*     |
| Password    | El token `ghp_...` generado en el paso anterior      |
| ID          | `github-grupo12`                                     |
| Description | `Token GitHub Grupo 12 - Integracion Continua`       |

**5.4.** Clic en **Create**.

## Paso 6 — Exponer Jenkins a Internet mediante ngrok

Jenkins corre en `localhost` y GitHub necesita poder llegar a él desde Internet para enviar los webhooks. Para resolver esto usamos un túnel ngrok.

**6.1.** Descargar el ejecutable de ngrok desde <https://dashboard.ngrok.com/get-started/setup/windows>, extraerlo y dejarlo en una carpeta accesible.

**6.2.** Configurar el authtoken (obtenerlo desde <https://dashboard.ngrok.com/get-started/your-authtoken>):

```bash
.\ngrok.exe config add-authtoken [TU_TOKEN_NGROK]
```

**6.3.** Levantar el túnel hacia el puerto 8081 de Jenkins:

```bash
.\ngrok.exe http 8081
```

Anotar la URL pública que aparece en la línea `Forwarding`, por ejemplo:

```
Forwarding   https://concave-canal-suspend.ngrok-free.dev -> http://localhost:8081
```

> Importante: dejar la ventana de ngrok abierta mientras se usa Jenkins. Si se cierra, el túnel se interrumpe.

## Paso 7 — Configurar el webhook en GitHub

**7.1.** Acceder a <https://github.com/ArlinsonMauricioCangrejo/INTEGRACI-N-CONTINUA-GRUPO-12/settings/hooks> y dar clic en **Add webhook**.

**7.2.** Completar:

| Campo            | Valor                                                          |
|------------------|----------------------------------------------------------------|
| Payload URL      | `https://[URL-NGROK]/github-webhook/` *(con la barra final)*  |
| Content type     | `application/json`                                             |
| SSL verification | `Enable SSL verification`                                      |
| Events           | `Just the push event`                                          |
| Active           | Marcado                                                        |

**7.3.** Clic en **Add webhook**.

**7.4.** GitHub envía un ping de prueba inmediato. Si todo está bien, el webhook aparece con un ícono verde y el mensaje *"Last delivery was successful"*.

## Paso 8 — Crear el pipeline en Jenkins

**8.1.** Desde el dashboard de Jenkins, dar clic en **+ Nueva Tarea**.

**8.2.** Ingresar `ticket-system-pipeline` como nombre, seleccionar **Pipeline** y dar clic en **OK**.

**8.3.** En la pantalla de configuración:

- **Description**: `Pipeline CI/CD del Sistema de Gestion de Tickets - Grupo 12`
- Marcar **GitHub project** y poner la URL del repositorio.
- En **Build Triggers**: marcar **"GitHub hook trigger for GITScm polling"**.
- En la sección **Pipeline**:
  - **Definition**: `Pipeline script from SCM`
  - **SCM**: `Git`
  - **Repository URL**: `https://github.com/ArlinsonMauricioCangrejo/INTEGRACI-N-CONTINUA-GRUPO-12.git`
  - **Credentials**: seleccionar `github-grupo12` (la creada en el Paso 5).
  - **Branches to build**: `*/main`
  - **Script Path**: `Jenkinsfile`

**8.4.** Clic en **Save**.

## Paso 9 — Ejecutar el pipeline

**9.1.** Disparo manual: desde la página del job, clic en **Construir ahora**.

**9.2.** Disparo automático: hacer un push al repositorio:

```bash
git add .
git commit -m "Disparo automatico del pipeline"
git push origin main
```

A los pocos segundos Jenkins detecta el push y arranca un nuevo build automáticamente. Esto se confirma observando:

- La consola de ngrok muestra `POST /github-webhook/  200 OK`.
- El dashboard de Jenkins muestra un nuevo build en `Builds`.

## Stages del Jenkinsfile

| # | Stage         | Propósito                                                              |
|---|---------------|------------------------------------------------------------------------|
| 1 | Checkout      | Descarga la última versión del código desde GitHub.                    |
| 2 | Build         | Construye las imágenes Docker del backend y frontend.                  |
| 3 | Test          | Ejecuta la suite de 13 pruebas pytest en una instancia descartable.    |
| 4 | Deploy        | Reconstruye y recrea los contenedores frontend y backend en producción con `docker compose up -d --build` (CD real — actualizado en la Entrega 3). |
| 5 | Health Check  | Valida que el API responde correctamente en `/api/health`.             |

Un pipeline completo dura entre 1 y 3 minutos según el cacheo de capas Docker.

## Solución de problemas comunes

| Síntoma en el log de Jenkins | Causa | Solución |
|------------------------------|-------|----------|
| `docker: not found` | El CLI de Docker no está instalado en el contenedor Jenkins | Repetir el Paso 3 |
| `compose build requires buildx 0.17.0 or later` | Falta el plugin buildx | Instalar buildx (incluido en el Paso 3) |
| `Container "ticket-db" is already in use` | Conflicto con el stack ya corriendo | El `Jenkinsfile` actual usa `docker run` directo para los tests, evitando este conflicto |
| `permission denied while connecting to Docker socket` | Permisos del socket | Dentro del contenedor: `chmod 666 /var/run/docker.sock` |
| `is not supported because it isn't reachable over the public Internet (localhost)` al crear el webhook | GitHub bloquea URLs hacia localhost | Usar ngrok según el Paso 6 |

---

# Entrega 3 — Travis CI y CloudBees (Semanas 7-8)

La Entrega 3 complementa el pipeline de Jenkins (Entrega 2) con dos herramientas adicionales y consolida el flujo CI/CD completo:

- **Travis CI**: servicio de integración continua en la nube (SaaS) que valida cada push de forma independiente a Jenkins, mediante su integración nativa con GitHub.
- **CloudBees**: capa de extensión empresarial que se instala como *plugins* sobre Jenkins. CloudBees adquirió Codeship (mencionado en la guía del módulo y ya discontinuado como servicio independiente), por lo que se replica su rol mediante estos plugins.

Además, en esta entrega el `Jenkinsfile` evolucionó de solo *verificar* a *desplegar* realmente (CD), y se corrigió el healthcheck del frontend.

## Parte A — Travis CI

### Pre-requisitos

- Cuenta de GitHub con el repositorio del proyecto.
- El archivo `.travis.yml` en la raíz del repositorio (ya incluido).

### Paso 1 — Registro y autorización

1. Ingresar a <https://app.travis-ci.com> e iniciar sesión con **Sign in with GitHub**.
2. Autorizar el acceso a la cuenta y a los repositorios mediante GitHub Apps.

### Paso 2 — Vincular el repositorio

Activar el repositorio `INTEGRACI-N-CONTINUA-GRUPO-12` desde el dashboard de Travis para que detecte los push.

### Paso 3 — El archivo `.travis.yml`

Travis lee este archivo de la raíz del repositorio para saber cómo construir y probar. A diferencia del `Jenkinsfile` (Groovy), está escrito en YAML declarativo:

```yaml
language: python
python:
  - "3.11"
services:
  - docker
env:
  - DATABASE_URL=sqlite:///./test.db FLASK_ENV=testing
install:
  - cd backend && pip install -r requirements.txt
script:
  - cd backend && pytest -v --tb=short
```

Travis ejecuta las 13 pruebas pytest sobre una base SQLite efímera, de forma totalmente independiente a Jenkins (verificación cruzada del mismo cambio).

### Paso 4 — Activar el plan educativo (GitHub Student Developer Pack)

Travis CI eliminó su plan gratuito para nuevos usuarios y exige un plan de pago. Para habilitar los builds sin costo:

1. Obtener el **GitHub Student Developer Pack** en <https://education.github.com/pack> con el correo institucional.
2. Activar **2FA** y completar el perfil de GitHub (requisitos de la verificación académica).
3. Solicitar a soporte de Travis (<support@travis-ci.com>) el plan educativo, indicando el handle de GitHub.

### Paso 5 — Disparar el build

Cada `git push` a `main` dispara automáticamente un build en Travis gracias a la integración nativa con GitHub. El estado se ve en el dashboard de Travis y en los *badges* del repositorio (`build passing`).

## Parte B — CloudBees (plugins sobre Jenkins)

Codeship dejó de operar como servicio independiente tras su adquisición por CloudBees. Se replica su rol instalando los plugins de CloudBees sobre la instancia de Jenkins:

1. **Administrar Jenkins → Plugins → Available plugins**.
2. Buscar e instalar **CloudBees CD** y **CloudBees Installation Manager** (versiones usadas: CloudBees CD `1.1.42` y CloudBees Installation `1.43`).
3. Marcar **Restart Jenkins when installation is complete**, o reiniciar el contenedor:
   ```bash
   docker restart ticket-jenkins
   ```
4. Verificar en **Administrar Jenkins → Plugins → Installed plugins** que aparezcan los plugins de CloudBees.

## Parte C — El Jenkinsfile ahora despliega (CD real)

En la Entrega 2 el stage **Deploy** solo verificaba que el stack estuviera corriendo. En la Entrega 3 se actualizó para **desplegar de verdad**:

- Se alineó `COMPOSE_PROJECT_NAME = 'ticket-system'` para que Jenkins opere sobre los mismos contenedores de producción y no sobre un proyecto paralelo.
- El stage **Deploy** ahora ejecuta `docker compose up -d --build frontend backend`, recreando los contenedores de aplicación con la última versión del código. La base de datos (`ticket-db`) se deja intacta a propósito, para preservar los tickets (persistencia).

También se corrigió el **healthcheck del frontend**: consultaba `http://localhost/frontend-health`, que dentro del contenedor se resolvía a IPv6 (`::1`) donde Nginx no escucha, marcándolo `unhealthy`. Se cambió a `http://127.0.0.1/frontend-health` (IPv4) y quedó `healthy`.

## Parte D — Laboratorio end-to-end (azul → verde)

Demostración del flujo completo: un cambio visible en el frontend que se despliega solo tras un push, validado en paralelo por Jenkins y Travis CI.

1. Levantar el stack y verificar los 4 contenedores saludables:
   ```bash
   docker compose up -d
   docker ps --filter "name=ticket-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
   ```
2. Abrir <http://localhost:8080> (interfaz **azul**, v1.0) y crear un ticket de ejemplo.
3. Modificar `frontend/html/index.html`: cambiar el color de marca a verde (`#047857`) y agregar el badge de versión `v2.0 Entrega 3`.
4. Publicar el cambio:
   ```bash
   git add .
   git commit -m "E3: frontend v2.0 verde - demostracion de despliegue continuo"
   git push origin main
   ```
5. El push dispara **en paralelo** dos pipelines: Jenkins (vía webhook a través de ngrok) y Travis CI (integración nativa con GitHub).
6. Jenkins ejecuta sus 5 stages (Checkout → Build → Test → Deploy → Health Check) y recrea el contenedor frontend con la versión verde.
7. Travis ejecuta `pytest` de forma independiente y marca el build como `passed`.
8. Ambos pipelines terminan en verde.
9. Refrescar <http://localhost:8080> con **Ctrl+F5** (refresco forzado): la interfaz ahora está **verde** con el badge `v2.0 Entrega 3`, y los tickets creados antes del push siguen disponibles (persistencia en PostgreSQL tras el redespliegue).

---

## Hoja de ruta del módulo

- **Semanas 1-2 (Foro):** estructura base del proyecto, repositorio en GitHub, MVP del backend. ✅
- **Semana 3 (Entrega 1):** arquitectura completa de tres contenedores Docker comunicados. ✅
- **Semana 5 (Entrega 2):** Jenkins como orquestador del pipeline de CI con webhook real desde GitHub vía ngrok. ✅
- **Semanas 7-8 (Entrega 3):** Travis CI (CI en la nube) + CloudBees (plugins sobre Jenkins, sucesor de Codeship), `Jenkinsfile` con despliegue real (CD), laboratorio end-to-end y documentación final. ✅
