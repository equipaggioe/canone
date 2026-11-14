r"""Build a piece in Java into the artifact: its jar and the dependencies it runs with.

    python3 scripts/java.py <piece> <main class> <output>

It reads <piece>/dependencies.txt, one `group:artifact:version sha256` per line, downloads each
jar from Maven Central and fails before writing it if its SHA-256 is another. It compiles every
.java of <piece>/src/ for Java 21 and writes <output>/<piece>/<piece>.jar, which runs with
`java -jar` and finds its dependencies in <output>/<piece>/lib/.

From canone: plataformas/java.md.
"""

import argparse
import hashlib
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

MAVEN = "https://repo1.maven.org/maven2"
# The JRE of Debian 13 that runs the piece (java.md).
RELEASE = "21"
# The JAR File Specification: a line of the manifest has at most 72 bytes.
LINE = 72


def dependencies(piece: Path) -> list[tuple[str, str, str, str]]:
    """Return the group, artifact, version and SHA-256 of each dependency."""
    found = []
    for line in (piece / "dependencies.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        coordinates, digest = line.split()
        group, artifact, version = coordinates.split(":")
        found.append((group, artifact, version, digest))
    return found


def download(group: str, artifact: str, version: str, digest: str, lib: Path) -> str:
    """Download a jar into lib, only if it has its SHA-256, and return its name."""
    name = f"{artifact}-{version}.jar"
    url = f"{MAVEN}/{group.replace('.', '/')}/{artifact}/{version}/{name}"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest:
        raise SystemExit(f"{name} has the SHA-256 {actual}, not {digest}.")
    (lib / name).write_bytes(data)
    return name


def manifest(main: str, jars: list[str]) -> str:
    """Return the manifest that runs main with the jars of lib/."""
    lines = ["Manifest-Version: 1.0", f"Main-Class: {main}"]
    if jars:
        entry = "Class-Path: " + " ".join(f"lib/{jar}" for jar in jars)
        lines.append(entry[:LINE])
        rest = entry[LINE:]
        while rest:
            lines.append(" " + rest[: LINE - 1])
            rest = rest[LINE - 1 :]
    return "\n".join(lines) + "\n"


def main() -> None:
    """Download, compile and package the piece."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("piece", type=Path, help="the folder of the piece, like fingerprint")
    parser.add_argument("main", help="its class with main, like Afis")
    parser.add_argument("output", type=Path, help="the folder of the artifact, like dist")
    arguments = parser.parse_args()
    piece = arguments.piece
    target = arguments.output / piece.name
    lib = target / "lib"
    lib.mkdir(parents=True, exist_ok=False)
    jars = [download(*dependency, lib) for dependency in dependencies(piece)]
    sources = sorted(str(path) for path in (piece / "src").rglob("*.java"))
    if not sources:
        raise SystemExit(f"{piece}/src has no .java.")
    with tempfile.TemporaryDirectory() as folder:
        classes = Path(folder) / "classes"
        path = [str(lib / jar) for jar in jars]
        command = ["javac", "--release", RELEASE, "-d", str(classes)]
        if path:
            command += ["--class-path", os.pathsep.join(path)]
        subprocess.run([*command, *sources], check=True)
        description = Path(folder) / "MANIFEST.MF"
        description.write_text(manifest(arguments.main, jars), encoding="utf-8")
        jar = target / f"{piece.name}.jar"
        subprocess.run(
            ["jar", "--create", "--file", str(jar), "--manifest", str(description), "-C",
             str(classes), "."],
            check=True,
        )
    print(f"{jar}: {len(jars)} dependencies")


if __name__ == "__main__":
    main()
