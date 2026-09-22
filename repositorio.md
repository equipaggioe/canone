# Estructura y git

Lo que aplica a cualquier repositorio, tenga las piezas que tenga.

## Carpetas de primer nivel

El nombre de una pieza dice **dónde corre**, nunca con qué está hecha:

```
<dónde corre>[-<a quién sirve>]
```

El segundo término aparece solo cuando hay más de una pieza en el mismo lugar, y es una palabra del
dominio. Un producto con una sola web tiene `web/`; uno con tres tiene `web/`, `web-vendor/` y
`web-driver/`.

| Carpeta | Qué es |
|---|---|
| `server/` | El backend |
| `web/` | La web del usuario del producto |
| `panel/` | La web de la operación interna |
| `landing/` | El sitio público de presentación |
| `mobile/` | Cliente instalable en un teléfono |
| `desktop/` | Cliente instalable en una computadora |
| `packages/` | Código compartido entre piezas, como paquete instalable y no copiado. Dentro, el nombre es el del dominio a secas: `packages/mobile/`, `packages/protocol/` |
| `docs/` | `arquitectura/`, `adr/`, `planes/`. Nada más — ver [documentacion.md](documentacion.md) |
| `scripts/` | Lo que es del repositorio entero y `consola` no hace |
| `.consola/` | `params.json` y `config.env`. Lo lee `consola`; no se edita a mano |

`panel/` y `landing/` son las dos excepciones al patrón, y lo son porque la industria ya las nombra
así: un *admin panel* es la interfaz interna de gestión y una *landing page* es el sitio público.
`backoffice/` es sinónimo de `panel/` y no se usa; `frontend/`, `pwa/`, `flet_app/` y `app/` nombran
la tecnología o nada, y tampoco.

Un cliente que se instala es `mobile/` o `desktop/` según dónde se instala, no según con qué está
construido: Flet en un teléfono es `mobile/` y Flet en una computadora es `desktop/`.

Lo que necesita canal nativo va en un plugin local bajo `plugins/`.

Lo que `consola` hace no se duplica en un script del repositorio. Lo de una sola pieza va dentro de
ella, no en `scripts/`.

## Archivos del raíz

| Archivo | Contenido |
|---|---|
| `README.md` | Qué es el producto, qué piezas tiene, cómo se levanta cada una, enlace a `docs/` y a `canone` |
| `.gitignore` | Solo lo que no es de ninguna plataforma. Cada pieza tiene el suyo |
| `.gitattributes` | Se copia sin editar |
| `.github/workflows/ci.yml` | Un job por pieza que el repositorio tenga |

### `.gitignore`

Uno por plataforma, en la carpeta de la pieza:

| Archivo | Plantilla |
|---|---|
| Raíz | [`plantilla/.gitignore`](plantilla/.gitignore) |
| Cada pieza Python — `server/`, Flet, Qt | [`plantilla/python/.gitignore`](plantilla/python/.gitignore) |
| Cada superficie SvelteKit | [`plantilla/sveltekit/.gitignore`](plantilla/sveltekit/.gitignore) |
| Cada app Flutter | [`plantilla/flutter/.gitignore`](plantilla/flutter/.gitignore) |

Lo propio del repositorio se agrega al archivo de su pieza, con un comentario que diga por qué. El
raíz no cubre a las piezas: `verificar.py` falla si una carpeta con `package.json` no ignora
`node_modules/`.

## Git

- Rama `main`. Los cambios grandes van en rama y se integran cuando pasan CI.
- Un commit hace una cosa.
- **El mensaje va en español**, en imperativo y en una línea. Cuerpo solo si hay un porqué que el
  diff no muestra, y son dos o tres líneas.
- **Un cambio de comportamiento actualiza `docs/arquitectura/` en el mismo commit.**

## CI

Un job por pieza, y solo por las piezas que existen. Lo que corre cada job está en la página de su
plataforma.

**Una regla de `canone` que no rompe CI no es una regla, es una sugerencia.** Una convención nueva
se agrega junto con lo que la verifica.
