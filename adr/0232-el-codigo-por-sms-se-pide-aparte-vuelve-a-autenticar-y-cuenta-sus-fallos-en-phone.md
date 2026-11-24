# ADR-0232 · El código por SMS se pide aparte, vuelve a autenticar y cuenta sus fallos en `phone`

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `autenticacion.md`, `fastapi.md` y `plantilla/server/`

## Contexto

`autenticacion.md` decía que el código para entrar sigue las reglas del de Recuperación y cuenta sus
fallos en el teléfono, pero no cómo se pide, si sirve para volver a autenticarse, dónde viven los
fallos del teléfono ni qué pasa con el teléfono deshabilitado. Lo que recibe una cuenta de
administración está en el
[ADR-0233](0233-una-cuenta-de-administracion-cuenta-sus-fallos-como-cualquier-otra.md).

## Decisión

1. El código para entrar se pide en `POST /api/auth/sms/code`, como el del registro y el del cambio
   de teléfono.
2. Volver a autenticarse acepta el código: `POST /api/auth/reauth/sms/code` lo envía al teléfono de
   la cuenta y `POST /api/auth/reauth/sms` lo verifica.
3. Los fallos del teléfono viven en la tabla `phone`, con `Throttled`, una fila por cuenta con
   teléfono. El número sigue en `account`.
4. Cambiar el teléfono pone en cero sus fallos y lo vuelve a habilitar.
5. Con el teléfono deshabilitado o en espera, pedir el código responde 403 o 429 sin enviar el SMS.
6. Los 404 del código para entrar y los del código de recuperación cuentan juntos para bloquear la
   IP.
7. `METHODS` de la plantilla lleva los tres métodos, así el CI de Canone prueba todas
   sus rutas.
8. La base exige la fila en `phone` de cada cuenta con número, con un trigger de restricción
   diferido al commit.

## Consecuencias

- Un producto que solo usa el código por SMS puede cambiar el correo y el teléfono, que piden volver
  a autenticarse ([ASVS 5.0 §7.5.1](../fuentes/owasp/ASVS_V7_Session_Management.md)).
- Toda cuenta con teléfono tiene su fila en `phone`: la crean el registro y el cambio de teléfono,
  y un camino nuevo que ponga un número sin ella, como el del administrador, falla al hacer commit
  en vez de dejar la cuenta sin entrar con el código.
- Una prueba que corre en una transacción que se deshace no dispara el trigger: la suya lo corre con
  `SET CONSTRAINTS ALL IMMEDIATE`.
- `openapi.json` de la plantilla suma las rutas del código por SMS.

## Descartado

- **Columnas del teléfono en `account`.** No reusan `Throttled`, que el login con contraseña y con
  passkey ya comparten.
- **Dejar la fila solo a cargo del código.** Una cuenta sin su fila respondería 404 al pedir el
  código, sin error en ningún lado.
- **Mover el número a `phone`.** Se pierde el CHECK de que la cuenta tiene correo o teléfono, y cada
  búsqueda por teléfono necesita un join.
- **Sin volver a autenticarse con el código.** Un producto que solo usa el código no podría cambiar
  el correo ni el teléfono.
- **Que el teléfono nuevo conserve los fallos.** Un teléfono deshabilitado tiene que volver a
  vincularse para servir ([NIST SP 800-63B-4 §3.2.2](../fuentes/nist/sp800-63b-4.txt)), y otro número
  es otro autenticador.
- **Enviar el SMS a un teléfono deshabilitado o en espera.** No sirve para entrar: el login lo
  rechaza sin mirar el código.
- **Un contador de 404 por ruta.** Duplica lo que una IP puede enumerar.
