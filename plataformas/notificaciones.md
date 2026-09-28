# Notificaciones

Push y correo.

## Push móvil

Estándares: [*Firebase Cloud Messaging message types*](../estandares/firebase/set-message-type.md),
[*Send a message using Firebase Admin SDK*](../estandares/firebase/admin-sdk.md),
[*Best practices for FCM registration management*](../estandares/firebase/manage-tokens.md) y
[*FCM Error Codes*](../estandares/firebase/error-codes.md).

- Android y Flutter reciben push por FCM.
- El servidor envía con el Admin SDK de Python desde `asyncio.to_thread`. El SDK es síncrono.
- Cada mensaje lleva `notification`, que el sistema muestra con la app cerrada, y `data` con la
  ruta que abre al tocarlo.

## Web Push

Estándares: [*Push API*](../estandares/w3c/push-api.html) de W3C,
[RFC 8030](../estandares/rfc/rfc8030.txt), [RFC 8291](../estandares/rfc/rfc8291.txt) y
[RFC 8292](../estandares/rfc/rfc8292.txt).

- La web recibe push por el estándar, con VAPID, y el servidor envía con pywebpush. El navegador no
  carga un SDK de terceros y la CSP queda en `'self'`.

## Correo

Estándares: [RFC 5322](../estandares/rfc/rfc5322.txt), [RFC 7208](../estandares/rfc/rfc7208.txt)
(SPF), [RFC 6376](../estandares/rfc/rfc6376.txt) (DKIM), [RFC 7489](../estandares/rfc/rfc7489.txt)
(DMARC), [RFC 8058](../estandares/rfc/rfc8058.txt) y, de Amazon SES,
[*Understanding email deliverability*](../estandares/aws-ses/send-email-concepts-deliverability.md),
[DKIM](../estandares/aws-ses/dkim.md), [*Using a custom MAIL FROM domain*](../estandares/aws-ses/mail-from.md),
[DMARC](../estandares/aws-ses/dmarc.md),
[la lista de supresión](../estandares/aws-ses/suppression-list.md) y
[*Monitor email sending using event publishing*](../estandares/aws-ses/monitor-using-event-publishing.md).

- El correo sale por SES con la API v2, desde `asyncio.to_thread`.
- Cada correo lleva una parte en texto y otra en HTML.
- Un correo que no responde a una acción del usuario lleva `List-Unsubscribe` y
  `List-Unsubscribe-Post`.
- Los rebotes y las quejas llegan por event publishing a un endpoint del servidor, que marca la
  dirección como inválida. La app sabe que el correo no llega y se lo dice al usuario.
