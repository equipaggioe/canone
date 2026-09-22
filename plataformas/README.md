# Plataformas

Una página por tecnología en uso. **Solo aplica la de lo que el repositorio realmente tenga.**

| Página | Cubre | En uso en |
|---|---|---|
| [fastapi.md](fastapi.md) | Layout de `server/`, capas, settings, sesión de base, el sobre de error, paginación, push, tests, lint | Los 6 |
| [postgres.md](postgres.md) | Tipos, alias de columna, enums, geografía, nombres, migraciones, borrado | Los 6 |
| [sveltekit.md](sveltekit.md) | Adaptador, layout de `src/lib`, UnoCSS, estado con runes, cliente de la API, i18n, tests | 15 superficies web |
| [flutter.md](flutter.md) | Layout de `lib/`, tokens de tema, estado, red, almacenamiento, analizador, trampas | navetta ×3, vettore |
| [flet.md](flet.md) | Layout de `src/`, `core/`, tokens de tema, cliente de la API, sesión, i18n, empaquetado | presenze, banditore ×2, cadenza |
| [qt.md](qt.md) | Layout, tokens y hoja de estilos generada, red sin congelar la ventana, hilos | consola, presenze/terminal, spazio/app |
| [despliegue.md](despliegue.md) | El contrato de `.consola/config.env`, Caddy generado, qué no se commitea | Los 6 |

## Cómo se agrega una plataforma

1. Se usa en un repositorio y funciona.
2. Se escribe su página **leyendo ese código**, no una guía ni una intención.
3. Si hay dos repositorios que ya la usan distinto, la página dice cuál se adopta y por qué, y la
   diferencia entra en [homologacion.md](../homologacion.md).

Una página no se escribe por adelantado para una tecnología que todavía no se estrenó, y **ninguna
página dice cuándo elegir una plataforma sobre otra**: eso se decide producto por producto.

## Lo que cruza plataformas

Dos cosas, y las dos tienen la misma forma en las cuatro plataformas de cliente:

| Qué | Regla |
|---|---|
| **El sobre de error** | Lo define [fastapi.md](fastapi.md) y cada cliente lo traduce a un error tipado con los mismos campos. `errorCode` es el contrato, `detail` es texto para mostrar |
| **Los tokens de diseño** | Un solo módulo por cliente, sin colores ni tamaños literales fuera de él. Si el producto tiene panel web, es la misma paleta y el archivo dice de cuál es espejo |
