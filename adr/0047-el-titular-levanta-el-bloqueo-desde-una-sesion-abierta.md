# ADR-0047 · El titular levanta el bloqueo desde una sesión abierta

- **Estado:** Aceptada. El punto 2 lo reemplaza el
  [ADR-0067](0067-la-autenticacion-sigue-a-nist-y-el-bloqueo-cuenta-fallos-consecutivos-con-esperas.md)
- **Fecha:** 2026-10-12
- **Alcance:** la sección «Autenticación» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

Reemplaza el punto 3 del
[ADR-0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md) en lo que el
segundo bloqueo dura para siempre. Así, cualquiera que supiera el correo o el teléfono de una cuenta
podía fallar 20 veces y dejar al titular fuera para siempre, lo que la sección V6.1 de ASVS pide
evitar.

## Decisión

1. El bloqueo cierra solo el login: las sesiones abiertas siguen.
2. El titular levanta el bloqueo, el de 30 minutos o el segundo, desde una sesión abierta.

## Consecuencias

- El aviso del bloqueo llega a una sesión que sigue viva, y desde ella el titular lo levanta.
- Un titular sin ninguna sesión abierta sigue bloqueado.
