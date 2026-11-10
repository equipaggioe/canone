# ADR-0134 · `uninstall.py` deshace la máquina en tres niveles: la base, la app y la máquina

- **Estado:** Aceptada; los puntos 4, 5 y 6 son propuesta
- **Fecha:** 2026-11-09
- **Alcance:** «Desinstalar» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

Canone instala una máquina con `packages.py`, `swap.py`, `uv.py`, `install.py`, `credentials.py` y
`deploy.py`, y no traía nada que lo deshiciera. Consola quitó su botón «Vaciar VPS» porque
reimplementaba la reversa de `install.py` y, contra una máquina de Canone, dañaba lo que no
entendía; quedó esperando un programa de Canone. Mientras tanto, la única forma de volver a empezar
era reinstalar la imagen desde el proveedor.

## Decisión

1. `plantilla/infra/uninstall.py <app> database|app|machine` corre como `root`. Cada nivel incluye
   al anterior, y `--dry-run` imprime lo que haría sin hacerlo.
2. `database` detiene el servidor y lo que lo arranca, y borra la base, sus tres roles, sus
   credenciales (`<app>/database_url` y `<app>-migrate/`), su línea de `pg_hba.conf` y de
   `pg_ident.conf`, los archivos de los usuarios y el dump. `install.py` los vuelve a crear.
3. `app` borra además cada unidad, sitio, credencial, cuenta y carpeta de la app.
4. *(propuesta)* `machine` borra además el swap, uv, lo que `install.py` escribe para toda la
   máquina, y purga los paquetes de `packages.py` con sus datos, **salvo `sudo`**: la máquina
   queda lista para correr `install.py` otra vez desde el principio.
5. *(propuesta)* Ningún nivel toca la cuenta que administra, sus llaves ni `00-<app>.conf` de ssh,
   y `root` sigue bloqueado: son la entrada, y sin ellos la máquina solo se recupera desde el
   proveedor.
6. *(propuesta)* Un paquete de `packages.py` se quita aunque la imagen ya lo trajera, y con él los
   de su familia (`postgresql*`, `valkey*`…), aunque alguien los instalara a mano. Antes de tocar
   nada, `machine` simula la purga de cada uno: el que se llevaría un paquete de fuera que alguien
   instaló a mano queda, con sus datos, y lo dice; y si los demás juntos todavía se llevarían
   alguno, falla. En el VPS de prueba de IONOS, purgar `python3` se llevaba `netplan.io`, que arma
   la red en cada arranque, y `cloud-init`, y sin `ca-certificates` apt no baja de su espejo HTTPS:
   quitarlos dejaba una máquina sin red al reiniciar, que solo se recupera desde la consola del
   proveedor, y sin apt para volver a instalar.

## Consecuencias

- Consola puede volver a tener el botón, que corre `uninstall.py` y no la reversa por su cuenta.
- Después de `database`, el servidor queda detenido y sus unidades habilitadas hasta correr
  `install.py`.
- Las cuentas de sistema que crean los paquetes (`postgres`, `caddy`, `valkey`, `turnserver`) quedan:
  `apt-get purge` no las borra.

## Descartado

- **Un nivel para lo que `install.py` escribe para toda la máquina, sin los paquetes:** es
  `machine` sin la purga, y reinstalar los paquetes tarda un minuto.
- **Reactivar `root` y borrar la cuenta que administra:** es el único paso que, cortado a la mitad,
  deja la máquina sin entrada, y `install.py` corre igual con `sudo` desde esa cuenta.
- **Quitar solo los paquetes que la imagen no traía:** `packages.py` no anota cuáles instaló, y el
  objetivo es una máquina lista para instalar otra vez, no la imagen exacta.
