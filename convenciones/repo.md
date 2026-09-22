# Convención: estructura del repositorio

## Un repositorio por producto, monorepo por dentro

Todas las superficies de un producto viven en el mismo repositorio y se despliegan juntas. No hay
versionado entre piezas ni contratos que sostener entre versiones: ver `principios.md`.

## Carpetas de primer nivel

Solo existen las que el producto tiene. El nombre es fijo.

| Carpeta | Qué es |
|---|---|
| `server/` | El backend. Siempre existe |
| `panel/` | Superficie web **del cliente**: la usa quien contrata o consume el producto |
| `backoffice/` | Superficie web **de la operación**: la usamos nosotros para operar el producto |
| `landing/` | Sitio público de presentación |
| `app/` | Cliente nativo o instalable |
| `docs/` | `arquitectura/`, `adr/`, `planes/`. Nada más — ver [documentacion.md](documentacion.md) |
| `scripts/` | Utilidades del repositorio, no de una superficie |
| `.consola/` | `params.json` y `config.env`. Lo lee `consola`; no se edita a mano |

**`panel` y `backoffice` no son sinónimos.** Un producto puede tener las dos (vettore) o una sola.
Si tiene una sola, el nombre dice para quién es, no cuál se escribió primero.

Una superficie con un nombre propio del dominio (`terminal/`, `vendor/`, `customer/`, `pwa/`) es
legítima cuando el dominio la nombra así; en ese caso su `README.md` dice qué es y a quién sirve.

## Archivos del raíz

| Archivo | Obligatorio | Contenido |
|---|---|---|
| `README.md` | Sí | Qué es el producto, cómo se levanta, enlace a `docs/` y a `canone` |
| `.gitignore` | Sí | Ver abajo |
| `.gitattributes` | Sí | Ver abajo |
| `.github/workflows/ci.yml` | Sí | Ver abajo |

### `.gitattributes`

Sin él, un archivo editado en Windows y otro en WSL aparecen como cambiados enteros, y un `.sh` con
CRLF no arranca. El de `plantilla/` es el bueno:

```
* text=auto eol=lf
*.png binary
*.jpg binary
*.pdf binary
*.woff2 binary
```

### `.gitignore`

El del raíz cubre lo que puede aparecer en cualquier carpeta, **incluido `node_modules/`**: hoy
solo está en el `.gitignore` de cada superficie web, así que una superficie nueva sin el suyo lo
sube. Lo específico de una superficie va en el `.gitignore` de esa superficie, con un comentario
que diga por qué.

Nunca se commitean: secretos (`.env`, `*service-account*.json`, certificados), artefactos de build,
caches, y media subida por personas.

## Git

- Rama `main`. Los cambios grandes van en rama y se integran cuando pasan CI.
- Un commit hace una cosa. El mensaje, en inglés e imperativo.
- **Un cambio de comportamiento actualiza `docs/arquitectura/` en el mismo commit.**

## CI

`ci.yml` corre en cada push a `main` y en cada pull request, con un job por superficie. El de
concordia es el modelo:

| Job | Pasos |
|---|---|
| `server` | `ruff check .`, `mypy app`, `pytest` |
| Cada superficie web | `npm ci`, `npm run check` (svelte-check), `npm run test:unit` si tiene, `npm run build` |

Los tests corren contra un schema dedicado del Postgres remoto, con la URL en un secret del
repositorio. Nunca contra el schema real.

**Una regla de `canone` que no rompe CI no es una regla, es una sugerencia.** Cuando se agregue una
convención nueva, se agrega junto con lo que la verifica.
