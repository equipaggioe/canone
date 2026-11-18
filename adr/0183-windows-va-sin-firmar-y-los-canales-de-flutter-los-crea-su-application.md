# ADR-0183 · Windows va sin firmar, y los canales de Flutter los crea su `Application`

- **Estado:** Aceptada. El usuario pidió no firmar si no hay un servicio propio o gratuito, y
  implementar los canales si la recomendación se mantenía al reevaluarla (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/transversal.md`](../plataformas/transversal.md), «Distribución», y
  [`plataformas/flutter.md`](../plataformas/flutter.md), «Push»

## Contexto

- El único servicio de firma gratuito para Windows es el de SignPath Foundation, y solo para
  proyectos de código abierto con licencia aprobada por la OSI: el certificado sale a nombre de la
  fundación, que figura como editor. Azure Artifact Signing y los certificados de las autoridades
  se pagan. Sin firma, SmartScreen avisa al descargar, y el usuario abre el instalador desde «Más
  información».
- Firebase dice que una app de Flutter necesita un canal de prioridad alta en Android, sin decir
  cómo se crea. La guía anterior de FlutterFire lo creaba con flutter_local_notifications. Android
  pide crear el canal al arrancar la app, y volver a crearlo con los mismos valores no hace nada.

## Decisión

1. **Los ejecutables y los instaladores de Windows van sin firmar** mientras no haya un servicio
   de firma propio o gratuito para el producto.
2. **Cada tipo de notificación tiene su canal, que crea al arrancar la `Application` de la app,
   en Kotlin**, y el manifiesto declara el canal por defecto de FCM.

Reemplaza el punto 5 del [ADR-0180](0180-cada-plataforma-se-escribe-como-si-hubiera-cuenta-y-cada-repositorio-elige-donde-publica.md)
en lo que esperaba un servicio de firma.

## Consecuencias

- Un producto de código abierto puede pedir la firma de SignPath Foundation: es otra decisión, que
  se toma en su repositorio.
- La app de Flutter tiene código de Kotlin propio, `App.kt`.

## Descartado

- **flutter_local_notifications:** un paquete más en el stack solo para crear los canales, que
  Android crea con una llamada.
- **Crear los canales en `MainActivity`:** un mensaje que llega antes de que el usuario abra la app
  no encuentra su canal.
