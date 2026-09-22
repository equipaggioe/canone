# Stack

Qué se usa, qué está a prueba y qué está prohibido. Una pieza entra aquí cuando se usa en un
repositorio y funciona; sale cuando se decide reemplazarla.

Estado verificado el 2026-09-22 leyendo los `requirements.txt`, `pyproject.toml` y `package.json`
de los seis repositorios.

## Adoptado

Es lo que se usa sin preguntar. Apartarse exige un ADR en el repositorio que se aparta.

### Servidor

| Pieza | Versión | Para qué |
|---|---|---|
| Python | 3.13 | |
| FastAPI | >= 0.115 | HTTP y WebSocket |
| Pydantic | v2 | Schemas de entrada y salida, en camelCase |
| pydantic-settings | v2 | Configuración desde el entorno |
| SQLAlchemy | 2.x, ORM async | Acceso a datos |
| asyncpg | | Driver async de la aplicación |
| psycopg[binary] | v3 | Driver sync, solo para Alembic y scripts |
| Alembic | >= 1.13 | Migraciones de esquema |
| uvicorn[standard] | | Servidor ASGI |
| argon2-cffi | | Hash de contraseñas |
| PyJWT[crypto] | >= 2.9 | Tokens |
| httpx | | Cliente HTTP |
| ruff + mypy + pytest | | Lint, tipos y tests |
| uv | | Instalación y lock de dependencias |

### Datos

| Pieza | Para qué |
|---|---|
| PostgreSQL | La base. Única |
| PostGIS + geoalchemy2 | Geografía, con `Geography(srid=4326)` |
| Redis | Solo donde hay varios procesos que compartir estado |

### Web

| Pieza | Versión | Para qué |
|---|---|---|
| SvelteKit 2 + Svelte 5 | | Todas las superficies web |
| adapter-static | | Todo se sirve con Caddy; no hay SSR |
| UnoCSS | 66.x | Estilos |
| TypeScript | | |
| Vite | | |
| vitest | | Tests de unidad de las superficies con lógica propia |

### Operación

| Pieza | Para qué |
|---|---|
| Caddy | Reverse proxy y TLS en el VPS |
| GitHub Actions | CI: lint, tipos, tests, build |
| consola | Despliegue y tareas por repositorio (`.consola/params.json`) |

## A prueba

Se usa en un repositorio y todavía no se sabe si se generaliza. **No se adopta en un repositorio
nuevo sin decidirlo.**

| Pieza | Dónde | Qué falta saber |
|---|---|---|
| Flutter | navetta (3 apps), vettore (`app/`) | Si es el cliente nativo único. Ver [adr/0008](adr/0008-un-solo-cliente-nativo.md) |
| Flet | presenze (`app/`, `terminal/`), banditore (`customer/`, `vendor/`), cadenza (`frontend/`) | Lo mismo |
| PWA con SvelteKit | concordia (`pwa/`) | Lo mismo |
| Vite 8 / TypeScript 6 / plugin-svelte 7 | vettore | Si el resto sube. Recomendado en `homologacion.md`, fila 15 |
| Stripe | concordia | Si es el cobro de todos o solo de ese producto |
| Resend | concordia | Ídem para correo transaccional |
| slowapi | concordia | vettore tiene su propio `rate_limit.py`: hay dos implementaciones del mismo problema |
| Celery | navetta | Es el único con cola de tareas. Está en `requirements.txt`; falta verificar si se usa |
| firebase-admin (FCM) | vettore, banditore | Push. concordia usa `pywebpush` en su lugar: dos mecanismos para lo mismo |

## Prohibido

| Pieza | Dónde está hoy | Qué se usa en su lugar | Por qué |
|---|---|---|---|
| `python-jose` | presenze | `PyJWT` | Sin mantenimiento desde 2021 y con vulnerabilidades publicadas. Los otros repositorios ya usan PyJWT |
| `passlib` | navetta | `argon2-cffi` directo | Sin mantenimiento desde 2020 y roto contra las versiones nuevas de bcrypt. Los otros cuatro repositorios ya usan `argon2-cffi` |
| `psycopg2-binary` | navetta | `psycopg[binary]` (v3) | psycopg2 está en mantenimiento pasivo; el resto ya está en v3 |
| `adapter-auto` | navetta/panel, presenze/panel, banditore/backoffice, cadenza/backoffice | `adapter-static` | Elige un adaptador de plataforma que no se usa |
| Un ORM sync en la aplicación | — | SQLAlchemy async | El servidor entero es async |
| `requirements.txt` como fuente de dependencias | los 6 | `pyproject.toml` + `uv.lock` | No fija versiones de forma reproducible |

## Tensiones abiertas

No son divergencias entre repositorios sino reglas que chocan entre sí. Requieren decisión.

| Tensión | Detalle |
|---|---|
| Redis opcional en concordia | `requirements.txt` documenta que Redis «solo se importa si `REDIS_URL` está definida: un despliegue de un solo proceso funciona sin tener Redis levantado». Es exactamente el degradado silencioso que `principios.md` prohíbe: con dos workers y sin `REDIS_URL`, los WebSocket se parten sin que nada falle. O Redis es obligatorio, o arrancar con más de un worker sin Redis tiene que reventar al arranque |
| Dos mecanismos de push | FCM (vettore, banditore) y Web Push (concordia). Puede ser legítimo —uno es app nativa y el otro navegador— pero no está escrito en ningún lado que esa sea la regla |
| Dos limitadores de tasa | `slowapi` (concordia) y `core/rate_limit.py` propio (vettore) |
