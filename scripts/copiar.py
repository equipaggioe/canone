"""Copia a un repositorio los archivos canónicos de la plantilla que le faltan o que se separaron.

Sin --aplicar solo los nombra. Son los que compara verificar.py: los que se completan no se tocan.

    python scripts/copiar.py ../<repo>                       # qué crearía y qué reemplazaría
    python scripts/copiar.py ../<repo> --aplicar
    python scripts/copiar.py ../<repo> --cuentas --aplicar   # también los de las cuentas, en un servidor sin ellas

No reemplaza un archivo con cambios sin commit, ni uno que git no sigue: lo que tenía se perdería.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from verificar import comparar, copias


def sin_commit(repo: Path, nombres: list[str]) -> list[str]:
    """Los archivos cuyo contenido no está en el último commit."""
    if not nombres:
        return []
    seguidos = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", *nombres],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.split("\0")
    cambiados = subprocess.run(
        ["git", "-C", str(repo), "diff", "-z", "--name-only", "--relative", "HEAD", "--", *nombres],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.split("\0")
    return [nombre for nombre in nombres if nombre not in seguidos or nombre in cambiados]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--cuentas", action="store_true", help="también los archivos de un servidor con cuentas")
    parser.add_argument("--aplicar", action="store_true", help="copia; sin esto solo nombra los archivos")
    args = parser.parse_args()
    repo: Path = args.repo

    # La consola de Windows no es UTF-8 y los nombres de archivo llevan acentos.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if not (repo / ".git").exists():
        raise SystemExit(f"{repo} no es la raíz de un repositorio de git.")
    if args.cuentas and not (repo / "server").is_dir():
        raise SystemExit(f"{repo.name} no tiene server/.")
    pendientes = [
        (nombre, canonico)
        for nombre, canonico in copias(repo, args.cuentas)
        if comparar(repo / nombre, canonico, nombre)
    ]
    for nombre, _ in pendientes:
        print(f"{'reemplaza' if (repo / nombre).exists() else 'crea'} {nombre}")

    perdidos = sin_commit(repo, [nombre for nombre, _ in pendientes if (repo / nombre).exists()])
    if perdidos:
        raise SystemExit(
            "No se copia nada: estos archivos se reemplazarían y lo que tienen no está en un commit: "
            + ", ".join(perdidos)
        )
    if args.aplicar:
        for nombre, canonico in pendientes:
            copia = repo / nombre
            copia.parent.mkdir(parents=True, exist_ok=True)
            # Con LF, como los deja .gitattributes.
            copia.write_bytes(canonico.read_bytes().replace(b"\r\n", b"\n"))
    print(f"{repo.name}: {len(pendientes)} archivos {'copiados' if args.aplicar else 'por copiar'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
