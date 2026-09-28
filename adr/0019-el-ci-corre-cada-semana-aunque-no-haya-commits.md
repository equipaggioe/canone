# ADR-0019 · El CI corre cada semana aunque no haya commits

- **Estado:** Propuesta
- **Fecha:** 2026-09-28
- **Alcance:** todos los repositorios; `repositorio.md`, `plantilla/.github/workflows/ci.yml` y
  `scripts/verificar.py`

## Contexto

pip-audit revisa en CI las vulnerabilidades conocidas de lo bloqueado
([plataformas/python.md](../plataformas/python.md)), y el CI solo corre con un push a `main` o con un
pull request. Una vulnerabilidad publicada después del último commit no la ve nadie: un repositorio
que pasa meses sin cambios nunca se vuelve a revisar, aunque el lock que tiene desplegado sea el
vulnerable.

## Decisión

1. El `ci.yml` de cada repositorio corre también cada semana, con el evento `schedule` de GitHub
   Actions, además de con cada push a `main` y cada pull request.
2. La corrida semanal es el workflow entero, no solo la auditoría.

## Consecuencias

- `verificar.py` falla si `.github/workflows/ci.yml` no tiene `schedule` con un `cron`. Cada
  repositorio agrega las dos líneas de la plantilla.
- La corrida semanal también encuentra lo que se pudre sin commits: una acción, una imagen de
  `ubuntu-latest` o una base de prueba que dejaron de funcionar.
- GitHub corre el `schedule` sobre el último commit de la rama por defecto, y avisa de un fallo a
  quien modificó por última vez la línea del `cron`
  ([*Events that trigger workflows*](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)).
- En un repositorio público, GitHub desactiva el `schedule` tras 60 días sin actividad. En uno
  privado no.
- Solo se audita lo que el CI ya audita: las dependencias de Python. Las superficies SvelteKit y
  las apps de Android y Flutter no tienen auditoría de dependencias en `canone`.

## Descartado

- **Dependabot o Renovate:** abren pull requests para subir versiones, que es otra cosa. Lo que
  falta es volver a revisar el lock que ya está.
- **Un workflow aparte solo con pip-audit:** duplica la instalación de cada pieza, que ya vive en
  `ci.yml`, y la copia se queda vieja.
- **Correrlo a diario:** una vulnerabilidad nueva no se arregla el mismo día en un repositorio que
  no está en producción, y siete corridas por semana son siete avisos del mismo fallo.
