r"""Build a piece in Java into the artifact: its jar and the dependencies it runs with.

    python3 scripts/java.py <piece> <main class> <output>
    python3 scripts/java.py --format <piece>

The first fails if a .java of <piece>/src/ does not have the format of google-java-format. It reads
<piece>/dependencies.txt, one `group:artifact:version sha256` per line, downloads each jar from
Maven Central and fails before writing it if its SHA-256 is another. It compiles every .java for
Java 21, with each warning as an error, and writes <output>/<piece>/<piece>.jar, which runs with
`java -jar` and finds its dependencies in <output>/<piece>/lib/. It deletes what an earlier run
wrote there before it starts.

The second gives each .java of <piece>/src/ the format of google-java-format.

From canone: plataformas/java.md.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

MAVEN = "https://repo1.maven.org/maven2"
# stack.md, «Java»: the JRE of Debian 13 that runs the piece.
RELEASE = "21"
# java.md, «Código»: every warning but serial fails the build.
LINT = ["-Xlint:all,-serial", "-Werror"]
# stack.md, «Java»: google-java-format, with what it runs with.
FORMATTER = (
    "com.google.googlejavaformat",
    "google-java-format",
    "2.0.0",
    "c78feb48c549fa7114b7ea11db3b456808f7b371ffe84e6643a44dd2f9588639",
)
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


def download(
    group: str, artifact: str, version: str, digest: str, lib: Path, suffix: str = ""
) -> str:
    """Download a jar into lib, only if it has its SHA-256, and return its name."""
    name = f"{artifact}-{version}{suffix}.jar"
    url = f"{MAVEN}/{group.replace('.', '/')}/{artifact}/{version}/{name}"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest:
        raise SystemExit(f"{name} has the SHA-256 {actual}, not {digest}.")
    (lib / name).write_bytes(data)
    return name


def sources(piece: Path) -> list[str]:
    """Return each .java of the piece."""
    found = sorted(str(path) for path in (piece / "src").rglob("*.java"))
    if not found:
        raise SystemExit(f"{piece}/src has no .java.")
    return found


def formatter(folder: Path) -> Path:
    """Download google-java-format into folder and return its jar."""
    return folder / download(*FORMATTER, folder, suffix="-all-deps")


def check_format(piece: Path, folder: Path) -> None:
    """Fail if a .java of the piece does not have the format of google-java-format."""
    jar = formatter(folder)
    checked = subprocess.run(
        ["java", "-jar", str(jar), "--dry-run", "--set-exit-if-changed", *sources(piece)]
    )
    if checked.returncode != 0:
        raise SystemExit(
            f"Those .java do not have the format of google-java-format: "
            f"python3 scripts/java.py --format {piece}"
        )


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


def build(piece: Path, main: str, output: Path) -> None:
    """Check, download, compile and package the piece into output/<piece>/."""
    target = output / piece.name
    if piece.resolve().is_relative_to(target.resolve()):
        raise SystemExit(f"{target} would delete the piece itself: choose another output.")
    if target.exists():
        shutil.rmtree(target)
    lib = target / "lib"
    lib.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as folder:
        work = Path(folder)
        check_format(piece, work)
        jars = [download(*dependency, lib) for dependency in dependencies(piece)]
        classes = work / "classes"
        command = ["javac", "--release", RELEASE, *LINT, "-d", str(classes)]
        if jars:
            command += ["--class-path", os.pathsep.join(str(lib / jar) for jar in jars)]
        subprocess.run([*command, *sources(piece)], check=True)
        description = work / "MANIFEST.MF"
        description.write_text(manifest(main, jars), encoding="utf-8")
        subprocess.run(
            ["jar", "--create", "--file", str(target / f"{piece.name}.jar"), "--manifest",
             str(description), "-C", str(classes), "."],
            check=True,
        )
    print(f"{target / piece.name}.jar: {len(jars)} dependencies")


def main() -> None:
    """Build the piece, or format its code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--format", action="store_true", help="format the code instead")
    parser.add_argument("piece", type=Path, help="the folder of the piece, like fingerprint")
    parser.add_argument("main", nargs="?", help="its class with main, like Afis")
    parser.add_argument(
        "output", type=Path, nargs="?", help="the folder of the artifact, like dist"
    )
    arguments = parser.parse_args()
    if arguments.format:
        if arguments.main or arguments.output:
            parser.error("--format takes only the piece")
        with tempfile.TemporaryDirectory() as folder:
            jar = formatter(Path(folder))
            command = ["java", "-jar", str(jar), "--replace", *sources(arguments.piece)]
            subprocess.run(command, check=True)
    elif arguments.main is None or arguments.output is None:
        parser.error("the main class and the output are required")
    else:
        build(arguments.piece, arguments.main, arguments.output)


if __name__ == "__main__":
    main()
