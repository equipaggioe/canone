# Plataformas

Una página por tecnología en uso. **Solo aplica la de lo que el repositorio realmente tenga.**

| Página | Cubre |
|---|---|
| [fastapi.md](fastapi.md) | Layout de `server/`, capas, settings, sesión de base, el sobre de error, paginación, tests, lint |
| [postgres.md](postgres.md) | Tipos, alias de columna, enums, geografía, nombres, migraciones, borrado |
| [sveltekit.md](sveltekit.md) | Adaptador, layout de `src/lib`, UnoCSS, estado con runes, cliente de la API, tests |
| [flutter.md](flutter.md) | Layout de `lib/`, tokens de tema, estado, red, almacenamiento, analizador, trampas |
| [flet.md](flet.md) | Layout de `src/`, `core/`, tokens de tema, cliente de la API, sesión, empaquetado |

## Cómo se agrega una plataforma

1. Se usa en un repositorio y funciona.
2. Se escribe su página **leyendo ese código**, no una guía ni una intención.
3. Si hay dos repositorios que ya la usan distinto, la página dice cuál se adopta y por qué, y la
   diferencia entra en `homologacion.md`.

Una página no se escribe por adelantado para una tecnología que todavía no se estrenó.

## Lo que cruza plataformas

Una sola cosa atraviesa todas las páginas: **el sobre de error del servidor**. Lo define
[fastapi.md](fastapi.md) y cada cliente lo consume igual —`errorCode` es el contrato, `detail` es
texto para mostrar— sin importar si es SvelteKit, Flutter o Flet.
