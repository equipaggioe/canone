# Estructura y git

Lo que aplica a cualquier repositorio, tenga las piezas que tenga.

## Carpetas de primer nivel

Cada producto tiene las que necesita. El nombre es lo que se fija, no la existencia.

| Carpeta | Qué es |
|---|---|
| `server/` | El backend |
| `panel/` | Superficie web **del cliente**: la usa quien contrata o consume el producto |
| `backoffice/` | Superficie web **de la operación**: la usamos nosotros para operar el producto |
| `landing/` | Sitio público de presentación |
| `app/` | Cliente instalable, en la tecnología que sea |
| `docs/` | `arquitectura/`, `adr/`, `planes/`. Nada más — ver [documentacion.md](documentacion.md) |
| `scripts/` | Utilidades del repositorio, no de una superficie |
| `.consola/` | `params.json` y `config.env`. Lo lee `consola`; no se edita a mano |

**`panel` y `backoffice` no son sinónimos.** Un producto puede tener las dos, y significan cosas
distintas: `panel/` es el cliente web del usuario final, `backoffice/` es la operación interna. Un
producto con una sola superficie usa el nombre que dice para quién es, no el que se escribió
primero.

Una superficie con nombre propio del dominio (`terminal/`, `vendor/`, `customer/`, `pwa/`) es
legítima cuando el dominio la nombra así; su `README.md` dice qué es y a quién sirve.

Varias piezas de la misma tecnología que comparten código extraen un paquete local instalable, no
copiado. Lo que necesita canal nativo va en un plugin local bajo `plugins/`.

## Archivos del raíz

| Archivo | Contenido |
|---|---|
| `README.md` | Qué es el producto, qué piezas tiene, cómo se levanta cada una, enlace a `docs/` y a `canone` |
| `.gitignore` | Base en [`plantilla/.gitignore`](plantilla/.gitignore). Lo propio del repositorio se agrega con un comentario que diga por qué |
| `.gitattributes` | Se copia sin editar |
| `.github/workflows/ci.yml` | Un job por pieza que el repositorio tenga |

### `.gitattributes`

Se copia sin editar. Sin él, un archivo editado en Windows y otro en WSL aparecen como cambiados
enteros y un `.sh` con CRLF no arranca.

### `.gitignore`

`node_modules/` va en el raíz, no solo en el de cada superficie web: dejarlo solo ahí hace que
cualquier pieza nueva sin su propio `.gitignore` lo suba.

Nunca se commitean: secretos (`.env`, `.consola/config.env`, `*service-account*.json`,
certificados), artefactos de build, caches, y media subida por personas.

## Git

- Rama `main`. Los cambios grandes van en rama y se integran cuando pasan CI.
- Un commit hace una cosa. El mensaje, en inglés e imperativo.
- **Un cambio de comportamiento actualiza `docs/arquitectura/` en el mismo commit.**

## CI

Un job por pieza, y solo por las piezas que existen. Lo que corre cada job está en la página de su
plataforma.

**Una regla de `canone` que no rompe CI no es una regla, es una sugerencia.** Una convención nueva
se agrega junto con lo que la verifica.
