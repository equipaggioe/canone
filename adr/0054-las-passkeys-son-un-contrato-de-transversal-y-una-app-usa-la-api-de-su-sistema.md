# ADR-0054 · Las passkeys son un contrato de transversal, y una app usa la API de su sistema

- **Estado:** Aceptada
- **Fecha:** 2026-10-15
- **Alcance:** la sección «Passkeys» de [plataformas/transversal.md](../plataformas/transversal.md#passkeys),
  [plataformas/fastapi.md](../plataformas/fastapi.md#passkeys) y
  [plataformas/android.md](../plataformas/android.md#passkeys); el servidor y sus clientes

## Contexto

«Passkeys» vivía solo en `fastapi.md`, con WebAuthn y el flujo de OAuth para apps nativas. Las dos
fuentes regulan también a la web y a las apps, y `plataformas/README.md` pide que lo que cumplen
juntas varias piezas vaya en `transversal.md`.

## Decisión

1. WebAuthn, RFC 6749 §4.1, RFC 7636 y RFC 8252 pasan a `transversal.md`. `fastapi.md` deja de
   citar NIST SP 800-63B-4: la autenticación sigue el nivel 1 de ASVS, como en el resto de la
   página, y sus reglas de passkeys son propias.
2. `android.md` cita los requisitos de Credential Manager: Digital Asset Links asocia el dominio
   con la app.
3. `transversal.md` cita la sección 2.1 de RFC 9700, que actualiza a RFC 6749 en los flujos con
   redirección.
4. Una app usa la passkey con la API de su sistema operativo cuando su framework la ofrece de forma
   oficial, y si no, en el navegador del sistema, según RFC 8252. `android.md` cita las guías de
   Credential Manager.
5. Una cuenta con passkey se recupera con el código para restablecer de «Contraseñas». La
   recuperación se aplica 24 horas después, sin cerrar las sesiones, y el titular la cancela desde
   la app.
6. El titular ve sus passkeys y borra la que quiera.
7. El challenge vive en Valkey y se borra al usarlo.

## Consecuencias

- El dominio de la web sirve `/.well-known/assetlinks.json`, con la huella del certificado de cada
  app de Android.
- La app de Android no pasa por el navegador ni por OAuth para iniciar sesión.
- El nivel 1 de ASVS no tiene requisitos de autenticación criptográfica (V6.7) ni de recuperación
  de un factor perdido (6.4.4). Las reglas de passkeys de `fastapi.md` no tienen fuente.

## Descartado

- **Credential Manager solo en Android:** iOS, Windows y macOS también tienen una API de passkeys.
  La regla depende de que el framework la ofrezca, no de la plataforma.
- **El navegador del sistema en todas las apps:** donde hay una API del sistema, la passkey se usa
  sin salir de la app.
- **Seguir citando NIST SP 800-63B-4 en «Passkeys»:** dos estándares de autenticación en la misma
  página, como el que el [ADR-0045](0045-el-login-y-las-contrasenas-siguen-el-nivel-1-de-asvs.md)
  ya sacó de «Contraseñas».
- **Recuperar con un código guardado y un código por correo o por SMS:** el usuario pierde el
  código guardado, y una cuenta con contraseña ya se recupera con un solo código.
- **Cerrar todas las sesiones al recuperar:** quien recupera con un correo robado dejaría al dueño
  fuera, sin enterarse.
- **Recuperar sin espera:** quien roba el correo entra antes de que el dueño vea el aviso.
- **Avisar por el correo o el teléfono:** la cuenta puede tener uno solo, y quien lo robó recibe el
  aviso.
