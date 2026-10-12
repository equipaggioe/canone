# ADR-0046 · La contraseña se restablece con un código por correo o por SMS

- **Estado:** Aceptada
- **Fecha:** 2026-10-12
- **Alcance:** la sección «Contraseñas» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

El [ADR-0044](0044-el-bloqueo-cuenta-en-una-ventana-y-el-titular-lo-ve-en-la-app.md) descartó
avisar de un bloqueo por correo o por SMS, porque son los canales más comunes del phishing. Quien
olvidó su contraseña no puede entrar a la app, y no tiene otro canal.

## Decisión

1. Una cuenta restablece su contraseña con un código que recibe, a su elección, en el correo o en
   el teléfono que registró.
2. La solicitud para restablecer responde 404 si la cuenta no existe, con el mismo bloqueo por IP
   que el 409 del registro.
3. El código tiene 6 dígitos y vence en 10 minutos, por correo y por SMS. Uno nuevo reemplaza al
   anterior, y el tercer intento fallido lo invalida.
4. Cada correo y cada número reciben un código por minuto, y hasta 5 por hora.

## Consecuencias

- El código viaja por canales donde abunda el phishing: es el riesgo de poder recuperar la cuenta.
- Seis dígitos son el mínimo de NIST para un código de recuperación, y 10 minutos su máximo por
  SMS. El correo usa el mismo plazo para que los dos canales funcionen igual.

## Descartado

- **Responder igual exista o no la cuenta**, como pide el *Forgot Password Cheat Sheet*. No
  protege nada: el registro ya dice si la cuenta existe.
