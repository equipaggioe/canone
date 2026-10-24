# ADR-0077 · Un VPS aloja un solo producto

- **Estado:** Aceptada
- **Fecha:** 2026-10-24
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md) y `plantilla/infra/`

## Contexto

Los ADR [0071](0071-cada-app-tiene-su-instancia-de-valkey-y-cada-superficie-su-host-en-caddy.md),
[0072](0072-cada-instancia-de-valkey-limita-su-memoria-y-thp-se-apaga-solo-para-valkey.md) y
[0075](0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) y «Procesos» suponían varias
apps en una máquina: un puerto propio para cada una, y una instancia de Valkey para que una no
leyera las claves de otra. Quien despliega maneja un solo producto por VPS.

## Decisión

1. Un VPS aloja un solo producto: su servidor y sus superficies web (`landing`, `web` y `panel`).
   No corre un segundo servidor.
2. El servidor escucha siempre en el puerto 8000: es una constante de la unidad, del Caddyfile y de
   `deploy.py`, e `install.py` no lo recibe.
3. La instancia `valkey-server@<app>` se conserva: sin TCP y con un socket que solo abre el grupo
   de la app, ningún otro proceso de la máquina lee sus claves.

## Consecuencias

- Los nombres `<app>` de las rutas y las unidades siguen: identifican el producto, no a un
  inquilino.
- Del ADR-0071 queda sin efecto el motivo del punto 1, y del ADR-0072, la consecuencia «una app que
  llena su instancia no le quita memoria a otra».
- Del ADR-0075 quedan sin efecto la primera consecuencia y el motivo de los dos descartes, que
  hablan de una máquina compartida, y el puerto deja de ir en `.consola/config.env`. Las decisiones
  del ADR-0075 siguen.

## Descartado

- **Un puerto declarado por producto:** no hay otro servidor con quien chocar.
- **La instancia `valkey-server` del paquete:** cambia su configuración de Debian, y la instancia
  propia ya está probada en el ADR-0072.
