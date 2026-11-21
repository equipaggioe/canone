# ADR-0208 · Las contraseñas siguen a ASVS V6, y los requisitos de Credential Manager dejan de ser fuente

- **Estado:** Aceptada. El usuario aprobó las recomendaciones que siguieron a la revisión del [ADR-0207](0207-autenticacion-deja-lo-que-tiene-una-sola-forma-el-titular-cierra-sus-sesiones-y-el-flujo-del-navegador-se-liga-a-una-cookie.md) y confirmó el punto 3 (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** [plataformas/autenticacion.md](../plataformas/autenticacion.md), «Passkeys» de [plataformas/android.md](../plataformas/android.md) y `fuentes/`

## Contexto

Por [Elección entre fuentes](../plataformas/README.md#elección-entre-fuentes), los documentos de OWASP cuentan como uno: son la fuente de unas 14 secciones de todas las páginas (Sesión, Token de acceso, WebSocket en tres páginas, Caddy, Procesos, Archivos, Correo y SMS, Pagos, Permisos, Registro de eventos, CSP, Componentes, Service worker). NIST es la de unas 7 (Código por SMS, Contraseñas, Cuentas, Passkeys, Recuperación, Firewall, SSH y Respaldos). Los dos tienen la prioridad 2. Gana OWASP en cada asunto donde uno de sus documentos resuelve la mayoría de las decisiones:

- **Contraseñas:** ASVS 5.0.0 V6 resuelve el mínimo de 8 (§6.2.1), el largo de 64 (§6.2.9), la composición (§6.2.5), la lista de bloqueo (§6.2.4, §6.2.11 y §6.2.12), ocultar y mostrar (§6.2.6), pegar y los gestores (§6.2.7), verificar sin cambios (§6.2.8), sin cambio periódico (§6.2.10) y sin pistas ni preguntas (§6.4.2). No resuelve quién la elige, el conteo de Unicode, NFC, la guía ni el cambio por compromiso.
- **Cuentas y Recuperación:** V6 deja los valores a la documentación (§6.1.1 y §6.3.1) o los pone en el nivel 3 (§6.3.5, §6.3.7 y §6.5.6). Siguen en NIST.
- **Código por SMS:** casi todas sus convenciones son propias; ni V6 ni NIST resuelven la mayoría. Sigue en NIST, que es el origen de la única adoptada.
- **Sesión:** sigue en ASVS V7, y la reautenticación de «Cuentas» (§7.5.1) es de ese asunto.

El *WebSocket Security Cheat Sheet* cumple «Cubre»: es el origen de 15 de las 26 convenciones de WebSocket de `fastapi.md`, `transversal.md`, `autenticacion.md` y `despliegue.md`, y varias de las propias son de otros asuntos, como el formato de los mensajes.

Los requisitos de Credential Manager son una guía de configuración: dicen qué hace falta para que Android verifique el dominio, y no toman posición entre formas que funcionan (Normativa). En «Aporta» contaban junto con las demás páginas de Credential Manager, que son una misma documentación.

En Chromium 157.0.8103.79, `ProtectionPolicyToCredProtect`, de `content/browser/webauth/authenticator_common_impl.cc`, pide `credProtect` 3 cuando el sitio no lo pide, `residentKey` es `required` y `userVerification` es `preferred`. Es la versión de Chrome con que se probó en el ADR-0207.

Las razones que salen de la página, porque las convenciones no se apartan de una fuente ni la endurecen:

- El hash de Android en la penúltima línea: el final de la última queda para la sintaxis futura del formato.
- Las direcciones de aviso: una cuenta con un solo medio también tiene dos.
- Las esperas: llegar a los 100 fallos lleva unos cuatro días, y el titular lo ve antes.
- El 404 de la recuperación: el registro ya revela si la cuenta existe.

## Decisión

1. «Contraseñas» sigue a ASVS 5.0 V6 y V7, y deja de citar a NIST. Lo que V6 no resuelve queda como convención propia: la elige el titular, cada punto de código cuenta como un carácter, la guía, y el cambio cuando hay evidencia de compromiso. Reemplaza el punto 2 del [ADR-0067](0067-la-autenticacion-sigue-a-nist-y-el-bloqueo-cuenta-fallos-consecutivos-con-esperas.md) en las contraseñas.
2. El mínimo de 8 caracteres es una elección de §6.2.1, no una excepción.
3. La contraseña se normaliza a NFC antes del hash y al verificarla, y así se aparta de §6.2.8: el mismo texto escrito en otro dispositivo puede llegar en otra forma Unicode.
4. Los requisitos de Credential Manager dejan de ser fuente y salen de `fuentes/`. La convención de `asset_statements` de `android.md` queda propia.
5. El `credProtect` de Chrome se enlaza en el código de Chromium 157.0.8103.79, en vez del correo de 2023.

## Consecuencias

- Una revisión de «Contraseñas» compara con ASVS V6, y V6 entra en `fuentes/`.
- «Cumplimiento» de `autenticacion.md` sigue sin poder escribirse: queda en [pendientes/](../pendientes/autenticacion-sin-cumplimiento.md).

## Descartado

- **Dejar «Contraseñas» en NIST:** el criterio de Elección le da el asunto a OWASP, y V6 lo resuelve en su mayoría.
- **Pasar «Cuentas» y «Recuperación» a V6:** V6 no fija los valores que esas secciones necesitan.
