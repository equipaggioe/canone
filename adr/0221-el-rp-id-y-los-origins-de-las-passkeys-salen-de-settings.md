# ADR-0221 · El RP ID y los origins de las passkeys salen de `Settings`

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `plataformas/autenticacion.md`, `fastapi.md` y `plantilla/server/`

## Contexto

El RP ID de una passkey es el dominio, y el servidor compara el `origin` contra una lista fija. Cada
máquina tiene su dominio, el que recibe `install.py`, y el origin de una app de Android depende de la
llave que la firma: la de depuración no es la de publicación. Con el dominio como constante del
código, una máquina con otro dominio no podría usar passkeys.

Se comprobó leyendo `verify_authentication_response` de `webauthn` 3.0.1 que no mira el user handle
y que compara el `signCount` antes que la firma: una aserción falsa con un `signCount` bajo
denunciaría una passkey clonada.

## Decisión

1. El dominio es `domain` de `Settings`, y es el RP ID.
2. Los origins son `https://<dominio>`, `https://app.<dominio>` y `https://panel.<dominio>`, y los
   de `app_origins` de `Settings`.
3. Las opciones del login se piden en `POST /api/auth/passkey/options`, y el servidor
   busca el challenge por el que trae `clientDataJSON`.
4. El servidor le pasa a la biblioteca el `signCount` en 0 y lo compara él después de
   la firma, y comprueba el user handle.
5. La contraseña y la passkey comparten las esperas y el límite de sus fallos, en
   `services/authenticators.py`.

## Consecuencias

- Cada despliegue escribe `domain` y `app_origins` en sus credenciales.
- Una passkey de una máquina no sirve en otra con otro dominio.

## Descartado

- **El dominio y los origins como constantes del código.** Una máquina con otro dominio, o una app
  firmada con la llave de depuración, no podría usar passkeys.
