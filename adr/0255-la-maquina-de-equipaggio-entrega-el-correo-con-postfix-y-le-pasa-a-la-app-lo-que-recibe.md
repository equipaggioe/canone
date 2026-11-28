# ADR-0255 · La máquina de Equipaggio entrega el correo con Postfix, y le pasa a la app lo que recibe

- **Estado:** Aceptada el 2026-11-19 por el desarrollador, en el plan de despliegue de equipaggio:
  Postfix de Debian con `install.py --mail`, su `main.cf` y su `master.cf`, el 25 con `mail.nft`,
  `smtp_discard_ehlo_keywords = dsn` y un certificado propio para STARTTLS. El 2026-11-28, también
  por el desarrollador: Postfix le pasa lo que recibe a un programa que lo manda a la API con un
  secreto de `install.py`. Los puntos marcados *(propuesta)* se eligieron al construirlo, sin
  preguntar.
- **Fecha:** 2026-11-28
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Correo», «Configuración»,
  «Firewall» y «Máquina»; `install.py`, `packages.py`, `credentials.py`, `uninstall.py`, `main.cf`,
  `master.cf`, `mail.nft` y `mail` de `plantilla/infra/`

## Contexto

Equipaggio entrega el correo de cada producto. Lo hacía con un cliente SMTP propio y recibía los
rebotes con un servidor SMTP propio en el 25. Comparado con RFC 5321 y con Postfix 3.10, ese
cliente reintenta demasiado pronto, no se rinde, no limita los envíos por destino y no entrega a un
servidor cuyo STARTTLS falla.

Con el Postfix 3.10.13 de Debian 13, comprobado en [scripts/infra/mail.sh](../scripts/infra/mail.sh):
Postfix manda al remitente un aviso `multipart/report` de cada resultado, `Action: relayed` o
`Action: failed`, también si el servidor del destinatario anuncia DSN, siempre que corra con
`smtp_discard_ehlo_keywords = dsn`. Sin esa opción le pasa `NOTIFY` a ese servidor y no avisa del
éxito; sin `disable_mime_output_conversion = yes`, pasa a quoted-printable un cuerpo de 8 bits para
un servidor que no anuncia `8BITMIME`.

Canone no tiene una unidad para un proceso que escucha en un puerto, como el servidor de rebotes.

## Decisión

1. Solo la máquina de Equipaggio entrega correo, con el Postfix de Debian que instala
   `install.py --mail <host>`. Las demás mandan el suyo por la API de Equipaggio.
2. Postfix avisa él mismo de cada entrega, y la app sabe el resultado de cada correo por esos
   avisos.
3. Postfix recibe en el 25 solo el correo para `<host>`, y se lo pasa a la app por loopback: un
   programa de `install.py` lo manda a la API con un secreto que genera `install.py`. Nada en
   Python abre el 25.
4. *(propuesta)* Un solo host: Postfix se presenta con él, y es el dominio de los avisos y de los
   rebotes. El PTR de la máquina, su registro A y su MX nombran lo mismo.
5. *(propuesta)* Postfix envía solo por IPv4.
6. *(propuesta)* El certificado de STARTTLS es el de `ssl-cert`.
7. *(propuesta)* El programa manda el mensaje a `POST /api/email-notices`, como `message/rfc822`,
   con `X-Original-To`, y sale con 75 si la app no responde con 2xx.

## Consecuencias

- La máquina tiene dos colas: la de la base, hasta pasarle el correo a Postfix, y la de Postfix.
- Si la app está caída, Postfix guarda lo que recibe y lo vuelve a intentar, hasta su
  `maximal_queue_lifetime`.
- El secreto queda en claro en el programa, que solo lee la cuenta de la app, como el de coturn en
  `turnserver.conf`.
- `main.cf` y `master.cf` quedan al desinstalar, como lo demás que `install.py` sobrescribe de un
  paquete.
- La exposición de la unidad de Postfix en `systemd-analyze security` no se midió: es la del
  paquete.

## Descartado

- **Seguir con el cliente SMTP propio:** reimplementa un MTA con menos de lo que pide RFC 5321.
- **Leer la bitácora de Postfix:** frágil; los avisos de entrega son el formato de RFC 3464.
- **Que Postfix guarde lo que recibe en una carpeta, y un worker la lea:** la unidad de los
  workers necesitaría una segunda carpeta de estado.
- **Una unidad para un proceso que escucha en un puerto de loopback:** suma un tipo de unidad a
  Canone para un solo producto.
- **Que el programa llame a la API sin secreto, por venir de loopback:** Caddy también llega por
  loopback.
