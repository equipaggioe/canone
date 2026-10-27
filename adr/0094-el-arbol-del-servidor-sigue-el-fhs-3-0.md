# ADR-0094 · El árbol del servidor sigue el FHS 3.0

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Proyecto» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

«Proyecto» dibujaba dónde va cada archivo del servidor sin citar ninguna fuente. El comando de la
receptora se había puesto en `/usr/local/libexec/` al implementar el
[ADR-0078](0078-el-respaldo-lo-pide-una-receptora-y-lo-guarda-su-rest-server.md), y la sección
4.9.2 del FHS 3.0 no deja en `/usr/local` otras carpetas que las que nombra, entre las que no está
`libexec`.

## Decisión

1. «Proyecto» cita del FHS 3.0 las secciones de `/etc`, `/run`, `/srv`, `/usr/lib`, `/usr/local` y
   `/var/lib`.
2. El comando de la receptora es `/usr/local/lib/<app>/backup-request`: la sección 4.6 deja los
   binarios internos en `lib`, y la 4.9 pone en `/usr/local` lo que instala quien administra.

## Consecuencias

- Debian 13 sigue el FHS 3.0, salvo las excepciones que nombra el capítulo 9 de la *Debian Policy*.
- La copia de `fuentes/` es la que publica Debian: refspecs.linuxfoundation.org rechaza la descarga.
