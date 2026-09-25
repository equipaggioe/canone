# -*- coding: utf-8 -*-
"""Comprueba que un repositorio cumpla las convenciones de canone.

    python scripts/verificar.py --repo ../navetta
    python scripts/verificar.py --todos ..

Cada comprobación cita el ADR que la fija. Falla con código 1 y la lista de incumplimientos: una
regla que no rompe CI es una sugerencia, no una regla.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CANONE = Path(__file__).resolve().parent.parent
PLANTILLA = CANONE / "plantilla"

CANONICOS = [
    Path("server/app/models/base.py"),
    Path("server/app/schemas/base.py"),
]

# Relativos a cada pieza Qt, que es la que declara pyside6 en sus dependencias.
CANONICOS_QT = [
    Path("ui/ruff.toml"),
    Path("tests/test_theme.py"),
    Path("tests/test_conventions.py"),
]

# Una pieza se llama por dónde corre; el sufijo, cuando hay varias en el mismo lugar, es del
# dominio. `panel` y `landing` son las dos excepciones, con el nombre que ya usa la industria.
PREFIJOS = ("server", "web", "mobile", "desktop")
FIJAS = {"panel", "landing", "packages", "docs", "scripts", "infra", "plugins"}


def nombre_valido(nombre: str) -> bool:
    if nombre in FIJAS:
        return True
    base, _, rol = nombre.partition("-")
    if base not in PREFIJOS:
        return False
    return rol.isidentifier() or not rol


def normalizar(texto: str) -> str:
    return texto.replace("\r\n", "\n").rstrip() + "\n"


# ADR-0008: una bitácora que se puede editar por HTTP no es una bitácora. Se busca por el nombre
# del archivo del router, que es como se nombran en los seis repositorios; un router que escriba
# una bitácora con otro nombre se escapa, y eso se revisa leyendo, no aquí.
BITACORAS = ("audit_log", "auth_log", "activity_log", "security_log", "event_log", "login_attempt")
ESCRITURA = ("@router.post", "@router.patch", "@router.put", "@router.delete")


def bitacoras_solo_lectura(servidor: Path) -> list[str]:
    fallas = []
    for carpeta in ("app/routers", "app/api/routers"):
        for router in (servidor / carpeta).glob("*.py"):
            if not any(nombre in router.stem for nombre in BITACORAS):
                continue
            texto = router.read_text(encoding="utf-8")
            verbos = sorted({v.split(".")[1] for v in ESCRITURA if v in texto})
            if verbos:
                fallas.append(f"ADR-0008: {carpeta}/{router.name} expone {', '.join(verbos)} sobre una bitácora")
    return fallas


def revisar(repo: Path) -> list[str]:
    fallas: list[str] = []
    tiene_servidor = (repo / "server").is_dir()

    for rel in CANONICOS:
        canonico = PLANTILLA / rel
        copia = repo / rel
        if not copia.exists():
            # Un repositorio sin server/ no tiene por qué tener los archivos canónicos.
            if tiene_servidor:
                fallas.append(f"ADR-0002: falta {rel}")
            continue
        if normalizar(copia.read_text(encoding="utf-8")) != normalizar(
            canonico.read_text(encoding="utf-8")
        ):
            fallas.append(f"ADR-0002: {rel} no coincide con el canónico de canone")

    for carpeta in sorted(p for p in repo.iterdir() if p.is_dir()):
        if carpeta.name.startswith("."):
            continue
        if not nombre_valido(carpeta.name):
            fallas.append(f"repositorio.md: {carpeta.name}/ no es un nombre de pieza")

    if not (repo / ".gitattributes").exists():
        fallas.append("repositorio.md: falta .gitattributes")

    if not (repo / ".gitignore").exists():
        fallas.append("repositorio.md: falta .gitignore en el raíz")

    if not (repo / "README.md").exists():
        fallas.append("repositorio.md: falta README.md en el raíz")

    if not (repo / ".github/workflows/ci.yml").exists():
        fallas.append("repositorio.md: falta .github/workflows/ci.yml")

    servidor = repo / "server"
    if servidor.is_dir():
        if (servidor / "requirements.txt").exists():
            fallas.append("ADR-0006: server/requirements.txt sigue existiendo")
        if not (servidor / "pyproject.toml").exists():
            fallas.append("ADR-0006: falta server/pyproject.toml")
        if (servidor / "pytest.ini").exists():
            fallas.append("ADR-0006: pytest.ini suelto; la configuración va en pyproject.toml")
        if (servidor / "app/api").is_dir() and (servidor / "app/routers").is_dir():
            fallas.append("plataformas/fastapi.md: hay app/api/ y app/routers/ a la vez")
        if not (servidor / ".gitignore").exists():
            fallas.append("repositorio.md: server/ no tiene su propio .gitignore")
        fallas.extend(bitacoras_solo_lectura(servidor))

    # SvelteKit: solo para las superficies web que existan.
    for paquete in repo.glob("*/package.json"):
        if "node_modules" in str(paquete):
            continue
        superficie = paquete.parent
        # El .gitignore de la superficie es lo único que ignora node_modules/: el del raíz
        # ya no lo tapa, así que el olvido tiene que romper CI.
        ignore = superficie / ".gitignore"
        if not ignore.exists() or "node_modules" not in ignore.read_text(encoding="utf-8"):
            fallas.append(
                f"repositorio.md: {superficie.name}/ no ignora node_modules/ en su .gitignore"
            )
        datos = json.loads(paquete.read_text(encoding="utf-8"))
        deps = {**datos.get("dependencies", {}), **datos.get("devDependencies", {})}
        if "@sveltejs/kit" not in deps:
            continue
        if "@sveltejs/adapter-auto" in deps:
            fallas.append(f"ADR-0007: {superficie.name}/ usa adapter-auto")
        if not (superficie / "uno.config.ts").exists():
            fallas.append(
                f"plataformas/sveltekit.md: {superficie.name}/ no tiene uno.config.ts"
                " (la config de UnoCSS no va dentro de vite.config.ts)"
            )

    # Qt: solo para las piezas que dependan de PySide6.
    for pieza in sorted(p for p in repo.iterdir() if p.is_dir() and not p.name.startswith(".")):
        declaraciones = [pieza / "pyproject.toml", pieza / "requirements.txt"]
        if not any(
            d.exists() and "pyside6" in d.read_text(encoding="utf-8").lower() for d in declaraciones
        ):
            continue
        for rel in CANONICOS_QT:
            copia = pieza / rel
            if not copia.exists():
                fallas.append(f"ADR-0002: falta {pieza.name}/{rel.as_posix()}")
            elif normalizar(copia.read_text(encoding="utf-8")) != normalizar(
                (PLANTILLA / "qt" / rel).read_text(encoding="utf-8")
            ):
                fallas.append(
                    f"ADR-0002: {pieza.name}/{rel.as_posix()} no coincide con el canónico de canone"
                )

    # Flutter: solo para las apps que existan.
    for pubspec in repo.glob("*/pubspec.yaml"):
        app = pubspec.parent
        if not (app / "analysis_options.yaml").exists():
            fallas.append(f"plataformas/flutter.md: {app.name}/ no tiene analysis_options.yaml")

    docs = repo / "docs"
    if docs.is_dir():
        permitidos = {"README.md", "arquitectura", "adr", "planes"}
        sueltos = sorted(p.name for p in docs.iterdir() if p.name not in permitidos)
        if sueltos:
            fallas.append(
                "documentacion.md: docs/ tiene archivos fuera de la convención: "
                + ", ".join(sueltos)
            )

    return fallas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--todos", type=Path, help="directorio que contiene los repositorios")
    args = parser.parse_args()

    # La consola de Windows no es UTF-8 y los nombres de archivo llevan acentos.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.todos:
        repos = [
            p
            for p in sorted(args.todos.iterdir())
            if (p / ".git").exists() and p.resolve() != CANONE and not p.name.startswith(".")
        ]
    elif args.repo:
        repos = [args.repo]
    else:
        parser.error("hace falta --repo o --todos")

    total = 0
    for repo in repos:
        fallas = revisar(repo)
        total += len(fallas)
        print(f"\n{repo.name}: {len(fallas)} incumplimientos")
        for falla in fallas:
            print(f"  - {falla}")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
