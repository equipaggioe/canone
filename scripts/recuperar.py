"""Copia una sesión de Claude Code cortada justo antes de una compactación.

Sin argumentos toma la sesión más reciente que se compactó, de cualquier proyecto, y la corta antes
de su última compactación. La copia es una sesión nueva; la original no se toca.

    python scripts/recuperar.py                 # la sesión compactada más reciente
    python scripts/recuperar.py <id>            # una sesión concreta
    python scripts/recuperar.py <id> --antes 2  # antes de la penúltima compactación
"""

import argparse
import json
import uuid
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"


def boundaries(path: Path) -> list[int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [i for i, line in enumerate(lines) if '"compact_boundary"' in line]


def find(session: str | None) -> Path:
    if session:
        matches = list(PROJECTS.glob(f"*/{session}*.jsonl"))
        if len(matches) != 1:
            raise SystemExit(f"Se esperaba una sesión con id {session}, y hay {len(matches)}")
        return matches[0]
    sessions = sorted(PROJECTS.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in sessions:
        if boundaries(path):
            return path
    raise SystemExit("Ninguna sesión tiene una compactación")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("session", nargs="?")
    parser.add_argument("--antes", type=int, default=1, help="1 es la última compactación")
    args = parser.parse_args()

    source = find(args.session)
    cuts = boundaries(source)
    if not 1 <= args.antes <= len(cuts):
        raise SystemExit(f"La sesión tiene {len(cuts)} compactaciones")
    cut = cuts[-args.antes]

    old_id = source.stem
    new_id = str(uuid.uuid4())
    out = []
    for line in source.read_text(encoding="utf-8").splitlines()[:cut]:
        entry = json.loads(line)
        if entry.get("sessionId") == old_id:
            entry["sessionId"] = new_id
        if entry.get("type") == "ai-title":
            entry["aiTitle"] = f"{entry['aiTitle']} (antes de compactar)"
        out.append(json.dumps(entry, ensure_ascii=False))
    (source.parent / f"{new_id}.jsonl").write_text("\n".join(out) + "\n", encoding="utf-8")

    print(f"Copia de {old_id}, en {source.parent.name}, hasta la línea {cut}")
    print(f"claude --resume {new_id}")


main()
