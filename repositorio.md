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
| `scripts/` | Solo si hace falta: utilidades del repositorio que no son de ninguna superficie |
| `.consola/` | `params.json` y `config.env`. Lo lee `consola`; no se edita a mano |

**`panel` y `backoffice` no son sinónimos.** Un producto puede tener las dos, y significan cosas
distintas: `panel/` es el cliente web del usuario final, `backoffice/` es la operación interna. Un
producto con una sola superficie usa el nombre que dice para quién es, no el que se escribió
primero.

Una superficie con nombre propio del dominio (`terminal/`, `vendor/`, `customer/`, `pwa/`) es
legítima cuando el dominio la nombra así; su `README.md` dice qué es y a quién sirve.

Varias piezas de la misma tecnología que comparten código extraen un paquete local instalable, no
copiado. Lo que necesita canal nativo va en un plugin local bajo `plugins/`.

### `scripts/`

Levantar, migrar, desplegar y ver logs se hacen desde `consola`. Lo que `consola` ya hace **no se
duplica** en un script del repositorio: dos formas de hacer lo mismo divergen.

`scripts/` es para lo que es de este repositorio y de nadie más: una corrección de datos que se
corre una vez, un generador de código, una carga inicial. Lo de una sola superficie va dentro de
ella (las migraciones del backend son de `server/`, no del raíz). La mayoría de los repositorios no
tiene la carpeta, y eso está bien: lo que se fija es el nombre para cuando aparezca el primero.

## Archivos del raíz

| Archivo | Contenido |
|---|---|
| `README.md` | Qué es el producto, qué piezas tiene, cómo se levanta cada una, enlace a `docs/` y a `canone` |
| `.gitignore` | Solo lo que no es de ninguna tecnología. Cada pieza tiene el suyo — ver abajo |
| `.gitattributes` | Se copia sin editar |
| `.github/workflows/ci.yml` | Lo que GitHub corre en cada push: un job por pieza que el repositorio tenga |

### `.gitattributes`

Le dice a git cómo tratar cada archivo: qué es texto —y con qué final de línea se guarda— y qué es
binario. Se copia sin editar. Sin él, un archivo editado en Windows y otro en WSL aparecen como
cambiados enteros aunque nadie tocó una línea, y un `.sh` guardado con CRLF no arranca.

### `.gitignore`

**Uno por pieza, no uno grande en el raíz.** El del raíz ignora solo lo que no es de ninguna
tecnología: editores, sistema operativo y secretos. Cada pieza ignora lo suyo, en su propia carpeta:

| Archivo | Ignora | Plantilla |
|---|---|---|
| `.gitignore` | `.vscode/`, `.idea/`, `.claude/`, `.DS_Store`, `.env`, claves y certificados | [`plantilla/.gitignore`](plantilla/.gitignore) |
| `server/.gitignore` | `__pycache__/`, `.venv/`, caches de ruff, mypy y pytest, `*.db` | [`plantilla/server/.gitignore`](plantilla/server/.gitignore) |
| `panel/.gitignore` y cada superficie web | `node_modules/`, `.svelte-kit/`, `build/` | [`plantilla/web/.gitignore`](plantilla/web/.gitignore) |

Una regla en dos archivos es dos fuentes de verdad: `node_modules/` se ignora en la superficie web
que lo genera y en ningún otro lado. Una superficie nueva que se olvide del suyo no está cubierta
por el raíz, y por eso `verificar.py` falla si una carpeta con `package.json` no tiene
`.gitignore`. Se prefiere que rompa CI antes que un raíz que tapa el olvido en silencio.

Lo propio del repositorio se agrega al archivo de su pieza, con un comentario que diga por qué.

Nunca se commitean, en ninguna pieza: secretos (`.env`, `.consola/config.env`,
`*service-account*.json`, certificados), artefactos de build, caches, y media subida por personas.

## Git

- Rama `main`. Los cambios grandes van en rama y se integran cuando pasan CI.
- Un commit hace una cosa.
- **El mensaje va en español**, en imperativo y en una línea: qué cambia, no cómo se llegó. El
  código está en inglés; el mensaje lo leo yo. Cuerpo solo si hay un porqué que el diff no muestra,
  y son dos o tres líneas. El relato de la sesión no va al historial.
- **Un cambio de comportamiento actualiza `docs/arquitectura/` en el mismo commit.**

## CI

`.github/workflows/ci.yml` es lo que GitHub corre solo en cada push a `main` y en cada pull
request: instala las dependencias de cada pieza y corre su lint, sus tipos, sus tests y su build en
una máquina limpia. Si algo falla, el pull request queda en rojo.

Un job por pieza, y solo por las piezas que existen. Lo que corre cada job está en la página de su
plataforma.

**Una regla de `canone` que no rompe CI no es una regla, es una sugerencia.** Una convención nueva
se agrega junto con lo que la verifica.
