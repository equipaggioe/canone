# ADR-0072 · Cada instancia de Valkey limita su memoria, y Transparent Huge Pages se apaga solo para Valkey

- **Estado:** Propuesta
- **Fecha:** 2026-10-23
- **Alcance:** «Valkey» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

«Valkey» cita *Valkey setup tips*, que pide `vm.overcommit_memory = 1`, apagar Transparent Huge
Pages, tanto swap como memoria y un `maxmemory` explícito. Ni la página ni `plantilla/infra/`
cumplían ninguno, y desde el
[ADR-0071](0071-cada-app-tiene-su-instancia-de-valkey-y-cada-superficie-su-host-en-caddy.md) varias
instancias comparten la memoria de una máquina.

## Decisión

1. `install.py` recibe el `maxmemory` de la instancia de la app, y la instancia conserva
   `noeviction`.
2. `vm.overcommit_memory = 1` va en `/etc/sysctl.d/valkey.conf`, y `install.py` lo aplica con
   `sysctl --system`.
3. Transparent Huge Pages no se apaga en la máquina: `disable-thp yes`, el valor por defecto de
   Valkey 8.1, las apaga para su proceso.
4. `install.py` falla si la máquina tiene menos swap que memoria.

## Consecuencias

- Al llenarse, una instancia rechaza las escrituras con un error: un código, un contador o un id de
  sesión revocada nunca se borra para hacer lugar.
- Una app que llena su instancia no le quita memoria a otra.
- Una máquina sin swap no puede instalar una app hasta tenerlo.
- Comprobado en Debian 13 con THP en `always`: con `disable-thp yes`, `/proc/<pid>/status` de
  `valkey-server` da `THP_enabled: 0`, y con `no`, `1` y el aviso de THP en el log.

## Descartado

- **Un `maxmemory` fijo en `valkey.conf`:** cada app guarda volúmenes distintos, y un valor por
  defecto ocultaría que nadie lo eligió.
- **Una política de desalojo como `allkeys-lru`:** borraría códigos y contadores, que no se pueden
  reconstruir.
- **`echo never` en `/sys/kernel/mm/transparent_hugepage/enabled`:** cambia todos los procesos de
  la máquina y no persiste sin otra unidad, cuando Valkey ya se excluye solo.
- **`/etc/sysctl.conf`:** Debian 13 ya no lo trae.
