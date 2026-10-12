# ADR-0045 · El login y las contraseñas siguen el nivel 1 de ASVS

- **Estado:** Aceptada
- **Fecha:** 2026-10-11
- **Alcance:** las secciones «Autenticación», «Código por SMS», «Contraseñas» y «Passkeys» de
  [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

Reemplaza el punto 1 del
[ADR-0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md), que hacía
seguir el login al *Authentication Cheat Sheet* de OWASP. La página lo citaba con seis partes
excluidas y dos contradicciones (el nombre de usuario y el 409 del registro), y algunas de sus
partes regulaban lo mismo que la sección 3.1.1 de NIST SP 800-63B-4 que citaba «Contraseñas»,
que a su vez había que contradecir en el largo mínimo.

## Decisión

1. «Autenticación» sigue las secciones V6.1 y V6.3 de ASVS 5.0, en el nivel 1.
2. «Contraseñas» sigue las secciones V6.2 y V6.4 de ASVS 5.0, en el nivel 1, en lugar de la
   sección 3.1.1 de NIST SP 800-63B-4.
3. El *Forgot Password Cheat Sheet* de OWASP se sigue, salvo *Security Questions*.
4. Recuperar una cuenta con passkey sigue lo que dice «Passkeys».
5. Cambiar el correo, el teléfono o una passkey pide volver a autenticarse. El correo o el teléfono
   se cambia con un código enviado al nuevo, y el viejo recibe un aviso. El que la cuenta no
   registró al nacer se agrega desde una sesión abierta, verificado con un código.
6. El login con contraseña responde el mismo error exista o no la cuenta.

## Consecuencias

- El mínimo de 8 caracteres, la cuenta sin nombre de usuario y el 409 del registro dejan de
  contradecir una fuente.
- La lista de bloqueo tiene al menos las 3000 contraseñas más comunes, y cambiar la contraseña pide
  la actual.
- Volver a autenticarse y el proceso para cambiar el correo los pedía el *Authentication Cheat
  Sheet*; ahora son reglas propias.
- Una cuenta que nació con un solo medio puede sumar el otro y restablecer su contraseña por los
  dos.

## Descartado

- **Cambiar el correo con un enlace.** Obliga a una página web o a un enlace que abra la app, el
  correo se lee a veces en otro dispositivo, y un enlace es lo que imita el phishing. Un código se
  escribe en la misma app, igual que el del teléfono.
- **El nivel 2 de ASVS.** Exige dos factores para entrar (6.3.3) y comparar con contraseñas
  filtradas (6.2.12), que obliga a consultar un servicio externo o a guardar su base.
- **La sección 3.1.1 de NIST SP 800-63B-4.** Pide 15 caracteres cuando la contraseña es el único
  factor, y está escrita para proveedores de identidad, no para aplicaciones.
- **Seguir con el *Authentication Cheat Sheet* de OWASP.** Seis partes excluidas, dos
  contradicciones y solapes con la fuente de «Contraseñas».
