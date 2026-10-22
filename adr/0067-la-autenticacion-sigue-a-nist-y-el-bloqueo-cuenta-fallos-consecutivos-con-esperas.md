# ADR-0067 · La autenticación sigue a NIST, y el bloqueo cuenta fallos consecutivos con esperas crecientes

- **Estado:** Aceptada
- **Fecha:** 2026-10-22
- **Alcance:** las secciones «Autenticación», «Código por SMS» y «Contraseñas» de
  [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

«Autenticación» y «Contraseñas» citaban el nivel 1 de ASVS 5.0 y el *Forgot Password Cheat Sheet*
de OWASP, y «Código por SMS» citaba NIST SP 800-63B-4: dos estándares de autenticación en la misma
página. ASVS y NIST son del mismo orden, y NIST cubre más del asunto: el límite de intentos, el
vínculo de autenticadores, los avisos y la recuperación de la cuenta.

El bloqueo contaba 10 fallos en 15 minutos. Quien probaba 9 cada 15 minutos nunca llegaba al
límite, unos 860 intentos por día sin fin, y 20 fallos en 45 minutos dejaban al titular fuera
hasta que lo levantara.

## Decisión

1. «Autenticación» cita de NIST SP 800-63B-4 las secciones 2.1.1, 2.1.2, 3.2.2, 4.1 y 4.6, y 2.2.1
   y 2.2.2 en las cuentas de administración. Reemplaza el punto 1 del
   [ADR-0045](0045-el-login-y-las-contrasenas-siguen-el-nivel-1-de-asvs.md).
2. «Contraseñas» cita las secciones 3.1.1, salvo cómo se guarda la contraseña, y 4.2 de NIST, y la
   sección *Argon2id* del *Password Storage Cheat Sheet*. Reemplaza los puntos 2 y 3 del ADR-0045.
3. El límite es de 100 fallos consecutivos por autenticador, y desde el quinto cada intento espera
   30 segundos, que se duplican hasta una hora. Reemplaza el punto 3 del
   [ADR-0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md).
4. El conteo vive en la base. Reemplaza el punto 2 del ADR-0044.
5. Las direcciones de aviso son el correo, el teléfono y el push a las apps con sesión abierta.
6. El titular vuelve a habilitar un autenticador desde una sesión abierta o, si es la contraseña,
   restableciéndola. Reemplaza el punto 2 del
   [ADR-0047](0047-el-titular-levanta-el-bloqueo-desde-una-sesion-abierta.md).
7. Cada fallo del código para restablecer cuenta entre los fallos consecutivos de la contraseña.

## Consecuencias

- Espaciar los intentos no sirve: solo un acceso correcto reinicia el conteo.
- Llegar a los 100 fallos lleva unos cuatro días, y el titular ve cada fallo en la app.
- El mínimo de 8 caracteres contradice a NIST, que pide 15 cuando la contraseña es el único factor.
- El conteo se escribe en la base en cada fallo.

## Descartado

- **Seguir con ASVS:** en el nivel 1 cubre menos, y no regula los códigos por SMS, así que obligaba a
  citar dos estándares de autenticación.
- **Contar los fallos en una ventana de tiempo:** quien prueba menos que el umbral en cada ventana
  prueba sin fin.
- **Dejar el conteo en Valkey:** sin ventana de tiempo, perderlo le regala al atacante 100 intentos
  nuevos.
