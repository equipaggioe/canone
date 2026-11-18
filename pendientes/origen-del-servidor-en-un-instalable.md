# Cómo sabe un instalable dónde está su servidor

Tema pendiente: **sin decidir**.

## Estado (verificado 2026-11-18)

`release.yml` construye cada instalable una vez por tag: el programa de `desktop/` y el AAB de cada app de `mobile/`. Canone no dice de dónde sale la dirección del servidor que usan.

| Repositorio | Cómo la recibe |
| :--- | :--- |
| posta, `desktop/` | Una constante, `SERVER_URL`, en `environment.py`, escrita a mano antes de compilar |
| posta, apps Flutter | `--dart-define=API_BASE_URL`, que el job `mobile` de la plantilla no pasa |
| presenze y comande, `desktop/` | La variable de entorno `SERVER_URL`, con un valor por omisión en presenze |

## Qué hay que decidir

- Si la dirección es una constante del código, la del dominio de producción, como pide «Errores» de [transversal.md](../plataformas/transversal.md#errores) para el `type` de un problema.
- Si el CI la escribe al construir, desde una variable del repositorio, y falla sin ella.
- Cómo apunta el mismo instalable a la máquina de pruebas o al servidor local.

## Cuándo se retoma

Antes de que un instalable salga a una máquina real: el de posta se publica desde su v0.0.2.
