# ADR-0102 · La hora la sincroniza systemd-timesyncd, e install.py falla si no está habilitado

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

`despliegue.md` no decía cómo se sincroniza la hora. El paquete `systemd` de Debian 13 solo
recomienda `systemd-timesyncd | time-daemon`, en el `debian/control` de systemd 257.13, así que una
máquina instalada sin recomendados puede no traer ninguno. Las credenciales temporales de TURN, las
sesiones y las fechas del journal dependen del reloj.

## Decisión

1. `systemd-timesyncd` está en la lista de paquetes de «Máquina».
2. `install.py` falla si `systemd-timesyncd.service` no está habilitado.

## Consecuencias

- `systemd-timesyncd` choca con `time-daemon`: instalarlo quita `chrony` o cualquier otro paquete de
  hora que traiga la máquina.
- `systemd-timesyncd` no corre en un contenedor (`ConditionVirtualization=!container`), así que el
  job `install` comprueba que `install.py` falla sin él, pero no que sincroniza.

## Descartado

- **`chrony`:** sirve hora a otras máquinas y la ajusta con más precisión, y la máquina solo necesita
  la suya. `systemd-timesyncd` es el que recomienda primero `systemd`, y es parte de systemd.
- **Aceptar cualquier `time-daemon`:** `install.py` tendría que conocer la unidad de cada uno.
