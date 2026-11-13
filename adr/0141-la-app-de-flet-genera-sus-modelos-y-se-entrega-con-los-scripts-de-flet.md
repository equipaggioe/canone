# ADR-0141 · La app de Flet genera sus modelos con datamodel-code-generator y se entrega como AAB, `setup.exe` y AppImage

- **Estado:** Aceptada
- **Fecha:** 2026-11-13
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), `plantilla/flet/` y los jobs de Flet
  de `ci.yml` y `release.yml`

## Contexto

`transversal.md` pide que cada cliente genere los modelos del cable del `openapi.json` y falle ante
un campo que no conoce. `flet build windows` y `flet build linux` dejan una carpeta, y
`despliegue.md` publica un solo archivo por sistema.

## Decisión

1. **Los modelos del cable los genera datamodel-code-generator**, en Pydantic v2, y las llamadas a
   la API se escriben a mano.
2. **Windows recibe el `setup.exe` de Inno Setup, y Linux, un AppImage**, con los scripts de la
   documentación de Flet.
3. **macOS recibe un DMG firmado y notarizado, e iOS va a la App Store, cuando haya cuenta de Apple
   Developer.** Hasta entonces, ninguno se construye.
4. **Las pruebas de integración usan `flet test`**, por pytest, en CI de Linux.

## Consecuencias

- El cliente de la API no se genera, a diferencia de Android y Flutter.
- CI de Flet instala Flutter y los paquetes de Linux para correr las pruebas.
- El instalador de Windows sale sin firmar: SmartScreen avisa hasta que haya un certificado.

## Descartado

- **openapi-python-client.** Genera también el cliente, sobre httpx, pero sus modelos son de `attrs`
  e ignoran un campo desconocido.
- **openapi-generator.** Necesita Java, y su cliente no usa httpx.
- **Un zip en Windows.** No instala, no se actualiza en su lugar y el usuario tiene que extraerlo
  antes de abrirlo.
- **`.deb` o `.rpm` en Linux.** Sirven a una familia de distribuciones cada uno; el AppImage, a todas.
