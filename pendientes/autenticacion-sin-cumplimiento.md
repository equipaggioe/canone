# «Cumplimiento» de autenticacion.md

Tema pendiente: **sin decidir**. `autenticacion.md` no tiene sección «Cumplimiento», y nada en Canone comprueba sus convenciones.

## Estado (verificado 2026-11-20)

| Pieza | Estado |
| :--- | :--- |
| `plataformas/autenticacion.md` | Sin «Cumplimiento» ni línea `Plantilla:` |
| `plantilla/server/` | Sin código de autenticación: solo `event_log`, `health` y los problemas |
| `scripts/verificar.py` | Solo comprueba las versiones de pwdlib, phonenumbers, PyJWT y `webauthn` (`PYPROJECT`), que son de `stack.md` |

Una fila de «Cumplimiento» necesita una herramienta que exista y haga cumplir entera su convención ([plataformas/README.md](../plataformas/README.md#criterios)). Sin código de autenticación en la plantilla, no hay contra qué correr una prueba.

## Qué se podría comprobar con pruebas

Convenciones que una prueba del servidor verifica sin un navegador ni una llave:

| Convención | Prueba |
| :--- | :--- |
| La cookie `__Host-session`, `Secure`, `HttpOnly`, `SameSite=Strict`, `Path=/` | Leer el `Set-Cookie` del login |
| Sin `code_challenge`, o con `plain`, responde `invalid_request` | Petición de autorización |
| Con `scope`, responde `invalid_scope` | Petición de autorización |
| El canje y el refresco llevan `Cache-Control: no-store` y `Pragma: no-cache` | Respuesta del endpoint de token |
| Un parámetro repetido o uno obligatorio que falta responde `invalid_request`, nunca 422 | Los dos endpoints |
| Un código presentado dos veces responde `invalid_grant` y borra la sesión | Canje doble |
| Un secreto de refresco que no es el vigente ni el anterior borra la sesión | Refresco con un token ya rotado |
| Un `POST` con la cookie sin `Origin` del servidor responde 403 | Petición sin `Origin` |
| El JWT con otra cabecera, otra firma o `exp` vencido se rechaza | Tokens armados a mano |
| Desde el quinto fallo, un intento antes de tiempo responde 429 | Fallos seguidos |

## Qué haría falta

| # | Cambio | Recomendación |
| :--- | :--- | :--- |
| 1 | Una plantilla de autenticación en `plantilla/server/`, con sus modelos, rutas y pruebas | Escribirla, porque la autenticación es igual en todos los repositorios y hoy cada uno la reescribe |
| 2 | «Cumplimiento» en `autenticacion.md`, con una fila por prueba | Después del punto 1, solo con pruebas que corran en el CI de Canone |
| 3 | `verificar.py` compara los archivos de autenticación que se copian sin editar | Igual que el resto de la plantilla del servidor |
