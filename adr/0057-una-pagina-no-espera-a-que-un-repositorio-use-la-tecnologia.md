# ADR-0057 · Una página no espera a que un repositorio use la tecnología

- **Estado:** Aceptada
- **Fecha:** 2026-10-16
- **Alcance:** `plataformas/`

## Contexto

El punto 2 del [ADR-0001](0001-el-estandar-vive-en-un-repositorio.md) decía que una página existe
porque la tecnología ya está en uso, y se escribe leyendo ese código. El
[ADR-0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md) reemplazó la segunda
mitad: una página se escribe desde sus fuentes, no desde el código. La primera mitad seguía en
`plataformas/README.md` como «Se agrega una página cuando la tecnología se estrena en algún
repositorio».

## Decisión

1. Una página de una tecnología se puede escribir aunque ningún repositorio la use todavía.
   Reemplaza la frase «Una página existe porque la tecnología ya está en uso» del punto 2 del
   ADR-0001.

## Consecuencias

- Puede haber páginas de tecnologías que ningún repositorio usa. Siguen aplicando solo a quien las
  usa.
