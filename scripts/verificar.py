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


def normalizar(texto: str) -> str:
    return texto.replace("\r\n", "\n").rstrip() + "\n"


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

    if not (repo / ".gitattributes").exists():
        fallas.append("convenciones/repo.md: falta .gitattributes")

    gitignore = repo / ".gitignore"
    if gitignore.exists() and "node_modules" not in gitignore.read_text(encoding="utf-8"):
        fallas.append("convenciones/repo.md: el .gitignore raíz no ignora node_modules/")

    if not (repo / "README.md").exists():
        fallas.append("convenciones/repo.md: falta README.md en el raíz")

    if not (repo / ".github/workflows/ci.yml").exists():
        fallas.append("convenciones/repo.md: falta .github/workflows/ci.yml")

    servidor = repo / "server"
    if servidor.is_dir():
        if (servidor / "requirements.txt").exists():
            fallas.append("ADR-0006: server/requirements.txt sigue existiendo")
        if not (servidor / "pyproject.toml").exists():
            fallas.append("ADR-0006: falta server/pyproject.toml")
        if (servidor / "pytest.ini").exists():
            fallas.append("ADR-0006: pytest.ini suelto; la configuración va en pyproject.toml")
        if (servidor / "app/api").is_dir() and (servidor / "app/routers").is_dir():
            fallas.append("convenciones/servidor-python.md: hay app/api/ y app/routers/ a la vez")

    for paquete in repo.glob("*/package.json"):
        if "node_modules" in str(paquete):
            continue
        datos = json.loads(paquete.read_text(encoding="utf-8"))
        deps = {**datos.get("dependencies", {}), **datos.get("devDependencies", {})}
        if "@sveltejs/adapter-auto" in deps:
            fallas.append(f"ADR-0007: {paquete.parent.name}/ usa adapter-auto")

    docs = repo / "docs"
    if docs.is_dir():
        permitidos = {"README.md", "arquitectura", "adr", "planes"}
        sueltos = sorted(p.name for p in docs.iterdir() if p.name not in permitidos)
        if sueltos:
            fallas.append(
                "convenciones/documentacion.md: docs/ tiene archivos fuera de la convención: "
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
