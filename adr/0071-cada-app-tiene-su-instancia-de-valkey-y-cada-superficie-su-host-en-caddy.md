# ADR-0071 · Cada app tiene su instancia de Valkey, y cada superficie, su host en Caddy

- **Estado:** Aceptada
- **Fecha:** 2026-10-23
- **Alcance:** «Caddy» y «Valkey» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

Varias apps comparten una máquina, y «Procesos» ya les daba un puerto propio. Valkey, en cambio,
era uno solo, y Caddy tenía reglas sin un archivo que las aplicara ni algo que las verificara.

## Decisión

1. Cada app tiene su instancia, `valkey-server@<app>`, la unidad que trae Debian 13, sin TCP y con
   un socket unix que solo abre el grupo de la app. La instancia del paquete queda apagada.
2. Cada superficie tiene su host: `landing` en `<dominio>`, `web` en `app.<dominio>` y `panel` en
   `panel.<dominio>`. En cada host, `/api/*` va al servidor de la app.
3. Los sitios de Caddy viven en `plantilla/infra/`, `install.py` los instala y el CI de canone los
   valida con `caddy validate`.
4. Caddy es el 2.6.2 de Debian 13. En `/api/*`, una petición cuyo `Content-Length` pasa el límite
   recibe 413 de Caddy antes de `request_body`, y el CI valida con ese mismo Caddy.
5. `Permissions-Policy` niega `camera`, `display-capture`, `geolocation` y
   `microphone`, y `install.py --allow` permite con `(self)` las que usa la app.
6. El límite de 10 MB es el de las peticiones `multipart/form-data`, y el de 1 MB, el
   del resto de `/api/*`.

## Consecuencias

- Una app no lee ni pisa las claves de otra, ni comparte memoria ni política de desalojo con otra.
- La API queda en el mismo origen que cada superficie, como pide
  [transversal.md](../plataformas/transversal.md#sesión): la cookie es de primera parte y no hace
  falta CORS. Cada superficie tiene su propia sesión.
- `install.py` sobrescribe `/etc/caddy/Caddyfile`, que es igual para todas las apps e importa los
  sitios de cada una.
- Cuando `request_body` corta un cuerpo que declara `Content-Length`, el 2.6.2 responde 502, y el
  cliente reintenta un 502; uno sin `Content-Length` lo corta con 413. Con el punto 4, los dos
  responden 413.
- Cada límite queda escrito dos veces en el Caddyfile, en `request_body` y en la expresión del 413,
  y se cambian juntos.
- Caddy envía `frame-ancestors 'none'` en su propia CSP, porque la de SvelteKit va en una etiqueta
  `meta`.

## Descartado

- **Un Valkey compartido con usuarios de ACL y prefijos `~<app>:*`:** obliga a prefijar cada clave
  en el código, y las apps siguen compartiendo memoria.
- **Bases numeradas de Valkey (`SELECT`):** no aíslan nada, porque cualquier app abre cualquier
  base.
- **La API en su propio subdominio:** contradice el mismo origen de transversal.md y obliga a
  CORS.
- **Las superficies como rutas de un solo host:** cada build de SvelteKit necesitaría `paths.base`,
  y la landing compartiría origen con la sesión de la web.
- **Caddy desde su repositorio oficial:** responde 413 sin el punto 4, pero suma un repositorio con
  su llave, y el servidor instala la versión de ese día, no la que valida el CI.
- **Caddy 2.11.2 de trixie-backports:** también responde 413 sin el punto 4, pero backports no
  tiene el soporte de seguridad de stable.
- **Aceptar el 502:** el cliente reintenta una subida que nunca va a pasar, y el 502 no se
  distingue de una caída del servidor.
- **Distinguir las rutas de subida por su path:** ninguna regla fija esos paths, y una subida
  siempre es `multipart/form-data`.
