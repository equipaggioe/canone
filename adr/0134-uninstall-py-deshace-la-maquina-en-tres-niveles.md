# ADR-0134 · `uninstall.py` deshace la máquina en tres niveles: la base, la app y la máquina

- **Estado:** Aceptada
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
4. `machine` borra además el swap, uv, los archivos que `install.py` escribe para toda la máquina y
   ningún paquete trae, y el túnel del journal. Los paquetes quedan, con lo que `install.py`
   sobrescribió en ellos, como el `Caddyfile` o `nftables.conf`: no se sabe qué traía la imagen.
   Dejar la máquina como la entrega el proveedor es reinstalarla desde su panel.
5. Ningún nivel toca la cuenta que administra, sus llaves ni `00-<app>.conf` de ssh,
   y `root` sigue bloqueado: son la entrada, y sin ellos la máquina solo se recupera desde el
   proveedor.

## Consecuencias

- Consola puede volver a tener el botón, que corre `uninstall.py` y no la reversa por su cuenta.
- Después de `database`, el servidor queda detenido y sus unidades habilitadas hasta correr
  `install.py`.
- Después de `machine`, `install.py` corre otra vez sobre la máquina sin reinstalar paquetes.

## Descartado

- **Purgar los paquetes de `packages.py`:** en el VPS de prueba de IONOS, purgar `python3` se
  llevaba `netplan.io`, que arma la red en cada arranque, y `cloud-init`, y sin `ca-certificates` apt
  no baja de su espejo HTTPS. Evitarlo pedía distinguir los paquetes de la imagen de los de
  `packages.py` y de sus dependencias, y el resultado igual no era la imagen del proveedor.
- **Reactivar `root` y borrar la cuenta que administra:** es el único paso que, cortado a la mitad,
  deja la máquina sin entrada, y `install.py` corre igual con `sudo` desde esa cuenta.
- **Quitar solo los paquetes que la imagen no traía:** pide que `packages.py` anote cuáles instaló,
  y la imagen exacta ya la da el proveedor.
