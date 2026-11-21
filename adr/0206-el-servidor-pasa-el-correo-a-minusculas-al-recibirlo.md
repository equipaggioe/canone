# ADR-0206 · El servidor pasa el correo a minúsculas al recibirlo

- **Estado:** Aceptada. El usuario eligió la opción recomendada (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** «Cuentas» de [plataformas/autenticacion.md](../plataformas/autenticacion.md)

## Contexto

`autenticacion.md` decía que el correo identifica la cuenta, pero no cómo se comparan dos correos. El [ADR-0204](0204-una-columna-espacial-dice-si-lleva-indice-un-texto-sin-mayusculas-se-guarda-en-minusculas-y-un-unique-con-null-dice-si-son-duplicados.md) fijó que un texto que se compara sin distinguir mayúsculas se guarda en minúsculas, con un `CHECK`.

[RFC 5321 §2.4](https://www.rfc-editor.org/rfc/rfc5321.txt): el dominio no distingue mayúsculas; la parte local «MUST BE treated as case sensitive», aunque «exploiting the case sensitivity of mailbox local-parts impedes interoperability and is discouraged». El *Authentication Cheat Sheet* de OWASP no trata las mayúsculas del identificador. comande, equipaggio y raccolta ya guardan el correo en minúsculas con `CHECK (email = lower(email))`.

## Decisión

1. El servidor pasa el correo entero a minúsculas al recibirlo, y así lo guarda, lo compara y le envía.

## Consecuencias

- Un buzón tiene una sola cuenta, aunque se escriba con mayúsculas distintas.
- En un servidor de correo que distinga mayúsculas en la parte local, el código de verificación no llega: se nota al registrarse.

## Descartado

- **Guardarlo como se escribió, y en otra columna en minúsculas para comparar:** dos columnas por correo para un caso que el RFC desaconseja.
- **Solo el dominio en minúsculas:** `Ana@` y `ana@` serían dos cuentas del mismo buzón.
