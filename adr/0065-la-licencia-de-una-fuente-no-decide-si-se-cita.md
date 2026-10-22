# ADR-0065 · La licencia de una fuente no decide si se cita

- **Estado:** Aceptada
- **Fecha:** 2026-10-21
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0063](0063-una-fuente-cumple-siete-requisitos-y-su-texto-se-lee-al-escribir-codigo.md)
pedía a una fuente siete requisitos, y el sexto era que su licencia permitiera copiar el texto en
`fuentes/`. Al revisar las fuentes de `fastapi.md`, el único texto que no lo cumplía, la
documentación de Stripe, fallaba además otros tres requisitos.

## Decisión

1. Sale el requisito «con licencia», y una fuente cumple los otros seis. Reemplaza esa parte del
   punto 1 del ADR-0063.

## Consecuencias

- Una fuente que cumple los seis requisitos se cita y se copia en `fuentes/` aunque su licencia no
  lo prevea.
- `despliegue.md` enlaza la documentación de Caddy en su sitio «porque su licencia no permite
  copiarla»; ese motivo ya no corre, y se revisa con esa página.

## Descartado

- **Conservar el requisito:** dejaría fuera una fuente buena por su licencia, sin que eso diga nada
  de si su texto es una buena convención.
