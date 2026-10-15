# -*- coding: utf-8 -*-
"""Comprueba que un repositorio cumpla las convenciones de canone.

    python scripts/verificar.py --repo ../navetta
    python scripts/verificar.py --todos ..

Cada comprobación cita el ADR que la fija. Falla con código 1 y la lista de incumplimientos: una
regla que no rompe CI es una sugerencia, no una regla.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

CANONE = Path(__file__).resolve().parent.parent
PLANTILLA = CANONE / "plantilla"

CANONICOS = [
    Path("server/alembic.ini"),
    Path("server/alembic/README"),
    Path("server/alembic/env.py"),
    Path("server/alembic/script.py.mako"),
    Path("server/src/app/database.py"),
    Path("server/src/app/tracing.py"),
    Path("server/src/app/openapi.py"),
    Path("server/src/app/models/__init__.py"),
    Path("server/src/app/models/base.py"),
    Path("server/src/app/models/ruff.toml"),
    Path("server/src/app/routers/problems.py"),
    Path("server/src/app/schemas/base.py"),
    Path("server/src/app/schemas/page.py"),
    Path("server/tests/test_conventions.py"),
]

# plataformas/fastapi.md: el driver es asyncpg y las pruebas async corren con AnyIO. Se revisa la
# dependencia declarada, así un paquete se ve aunque nadie lo importe todavía.
DESCARTADAS = {"psycopg", "psycopg2", "psycopg2-binary", "pytest-asyncio"}

# Relativos a la pieza; la clave es la dependencia que la identifica en su pyproject.toml.
CANONICOS_PIEZA = {
    "pyside6": ("qt", [Path("tests/test_theme.py")]),
    "flet": ("flet", [Path("tests/test_theme.py")]),
}

# Una pieza se llama por dónde corre; el sufijo, cuando hay varias en el mismo lugar, es del
# dominio. `panel` y `landing` son las dos excepciones, con el nombre que ya usa la industria.
PREFIJOS = ("server", "web", "mobile", "desktop")
FIJAS = {"panel", "landing", "packages", "docs", "scripts", "infra", "plugins", "brand"}


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
    for carpeta in ("src/app/routers",):
        for router in (servidor / carpeta).glob("*.py"):
            if not any(nombre in router.stem for nombre in BITACORAS):
                continue
            texto = router.read_text(encoding="utf-8")
            verbos = sorted({v.split(".")[1] for v in ESCRITURA if v in texto})
            if verbos:
                fallas.append(f"ADR-0008: {carpeta}/{router.name} expone {', '.join(verbos)} sobre una bitácora")
    return fallas


# principios.md, «Nombres»: a lo sumo cuatro palabras. Se revisan las funciones, los métodos y las
# clases; las variables y los atributos se revisan leyendo, porque ahí caen los campos de una API
# externa. Las excepciones que se detectan solas: las pruebas, lo marcado como override, el código
# generado (lo que git ignora, o lo que lo dice en su cabecera) y el sufijo de las clases de
# schemas/.
MAXIMO_PALABRAS = 4
PRUEBAS = {"tests", "test", "androidTest", "integration_test"}
PALABRA = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z0-9]+|[A-Z]+")
DECLARACION = {
    ".dart": re.compile(
        r"^\s*(?:(?:static|external|abstract)\s+)*(?:class\s+(\w+)"
        r"|(?:void|bool|int|double|num|dynamic|[A-Z]\w*)(?:<[^()=;]*>)?\??\s+(\w+)\s*(?:<[^()]*>)?\()",
        re.M,
    ),
    ".kt": re.compile(r"^\s*(?:[a-z]+\s+)*(?:class|interface|object|fun)\s+(?:<[^>]*>\s*)?(?:\w+\.)?(\w+)", re.M),
    ".ts": re.compile(
        r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function\*?\s+(\w+)|class\s+(\w+)"
        r"|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*(?::[^=]*)?=>)",
        re.M,
    ),
}
DECLARACION[".svelte"] = DECLARACION[".ts"]
OVERRIDE = {".dart": re.compile(r"@override\s*$"), ".kt": re.compile(r"\boverride\b"), ".ts": re.compile(r"\boverride\b")}
OVERRIDE[".svelte"] = OVERRIDE[".ts"]


def palabras(nombre: str) -> int:
    return len(PALABRA.findall(nombre.strip("_$")))


def generado(texto: str) -> bool:
    cabecera = texto[:500].lower()
    return "generated" in cabecera or "do not edit" in cabecera


def es_prueba(archivo: Path) -> bool:
    nombre = archivo.name
    return (
        bool(PRUEBAS & set(archivo.parts))
        or nombre.startswith("test_")
        or nombre == "conftest.py"
        or re.search(r"[._-](test|spec)\.\w+$", nombre) is not None
        or nombre.endswith(("_test.dart", "Test.kt"))
    )


def nombres_python(texto: str, en_schemas: bool) -> list[tuple[int, str, int]]:
    largos = []
    for nodo in ast.walk(ast.parse(texto)):
        if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        decoradores = {getattr(d, "id", getattr(d, "attr", "")) for d in nodo.decorator_list}
        if "override" in decoradores or nodo.name.startswith("test"):
            continue
        cuenta = palabras(nodo.name) - (1 if en_schemas and isinstance(nodo, ast.ClassDef) else 0)
        if cuenta > MAXIMO_PALABRAS:
            largos.append((nodo.lineno, nodo.name, cuenta))
    return largos


def nombres_otros(texto: str, sufijo: str) -> list[tuple[int, str, int]]:
    largos = []
    lineas = texto.splitlines()
    for coincidencia in DECLARACION[sufijo].finditer(texto):
        grupo = next(i for i, g in enumerate(coincidencia.groups(), 1) if g)
        nombre = coincidencia.group(grupo)
        linea = texto.count("\n", 0, coincidencia.start(grupo)) + 1
        anterior = lineas[linea - 2] if linea > 1 else ""
        if OVERRIDE[sufijo].search(lineas[linea - 1]) or OVERRIDE[sufijo].search(anterior):
            continue
        if nombre.startswith("test"):
            continue
        cuenta = palabras(nombre)
        if cuenta > MAXIMO_PALABRAS:
            largos.append((linea, nombre, cuenta))
    return largos


def listar(repo: Path) -> list[str]:
    """Lo que git sigue o seguiría: lo ignorado no es del repositorio."""
    return subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.splitlines()


def nombres_largos(repo: Path) -> list[str]:
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        sufijo = relativo.suffix
        archivo = repo / relativo
        if sufijo not in (".py", *DECLARACION) or es_prueba(relativo) or not archivo.is_file():
            continue
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        if generado(texto):
            continue
        if sufijo == ".py":
            try:
                largos = nombres_python(texto, "schemas" in relativo.parts)
            except SyntaxError:
                fallas.append(f"principios.md: {relativo.as_posix()} no se pudo leer como Python")
                continue
        else:
            largos = nombres_otros(texto, sufijo)
        for linea, nombre, cuenta in largos:
            fallas.append(f"principios.md: {relativo.as_posix()}:{linea} {nombre} tiene {cuenta} palabras")
    return fallas


# principios.md, «Nombres»: un identificador no repite el nombre del repositorio. Se revisa la
# configuración, donde el prefijo del proyecto es costumbre: las claves de los `.env.example`, los
# `String.fromEnvironment` de Dart y el `env_prefix` de pydantic-settings.
CONFIGURACION = {
    ".dart": re.compile(r"String\.fromEnvironment\(\s*['\"](\w+)['\"]"),
    ".py": re.compile(r"env_prefix\s*=\s*['\"](\w+)['\"]"),
}
CLAVE_ENV = re.compile(r"^\s*(?:export\s+)?([A-Za-z_]\w*)\s*=", re.M)


def configuracion_con_repositorio(repo: Path) -> list[str]:
    proyecto = re.sub(r"\W", "_", repo.resolve().name).upper()
    fallas = []
    for ruta in sorted(listar(repo)):
        relativo = Path(ruta)
        archivo = repo / relativo
        if relativo.name.endswith(".env.example"):
            patron = CLAVE_ENV
        elif relativo.suffix in CONFIGURACION:
            patron = CONFIGURACION[relativo.suffix]
        else:
            continue
        if not archivo.is_file():
            continue
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        for coincidencia in patron.finditer(texto):
            nombre = coincidencia.group(1)
            if proyecto in nombre.upper().strip("_").split("_"):
                linea = texto.count("\n", 0, coincidencia.start(1)) + 1
                fallas.append(
                    f"principios.md: {relativo.as_posix()}:{linea} {nombre} repite el nombre del repositorio"
                )
    return fallas


def dependencias(pyproject: Path) -> set[str]:
    datos = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    declaradas = list(datos.get("project", {}).get("dependencies", []))
    for grupo in datos.get("dependency-groups", {}).values():
        declaradas.extend(d for d in grupo if isinstance(d, str))
    nombres = set()
    for declarada in declaradas:
        nombre = re.match(r"[A-Za-z0-9._-]+", declarada)
        if nombre:
            nombres.add(re.sub(r"[._]", "-", nombre.group()).lower())
    return nombres


def comparar(copia: Path, canonico: Path, nombre: str) -> list[str]:
    if not copia.exists():
        return [f"ADR-0002: falta {nombre}"]
    if normalizar(copia.read_text(encoding="utf-8")) != normalizar(
        canonico.read_text(encoding="utf-8")
    ):
        return [f"ADR-0002: {nombre} no coincide con el canónico de canone"]
    return []


def revisar(repo: Path) -> list[str]:
    fallas: list[str] = []

    # Un repositorio sin server/ no tiene por qué tener sus archivos canónicos.
    if (repo / "server").is_dir():
        for rel in CANONICOS:
            fallas.extend(comparar(repo / rel, PLANTILLA / rel, rel.as_posix()))

    fallas.extend(comparar(repo / ".gitattributes", PLANTILLA / ".gitattributes", ".gitattributes"))

    for carpeta in sorted(p for p in repo.iterdir() if p.is_dir()):
        if carpeta.name.startswith("."):
            continue
        if not nombre_valido(carpeta.name):
            fallas.append(f"repositorio.md: {carpeta.name}/ no es un nombre de pieza")

    if not (repo / ".gitignore").exists():
        fallas.append("repositorio.md: falta .gitignore en el raíz")

    readme = repo / "README.md"
    if not readme.exists():
        fallas.append("repositorio.md: falta README.md en el raíz")
    elif not re.search(
        r"^Estado: en (desarrollo|producción)$", readme.read_text(encoding="utf-8"), re.M
    ):
        fallas.append("repositorio.md: README.md no declara si está en desarrollo o en producción")

    ci = repo / ".github/workflows/ci.yml"
    if not ci.exists():
        fallas.append("repositorio.md: falta .github/workflows/ci.yml")
    elif not re.search(r"^\s+schedule:\s*\n\s+- cron:", ci.read_text(encoding="utf-8"), re.M):
        fallas.append("ADR-0019: .github/workflows/ci.yml no corre cada semana (falta schedule)")

    servidor = repo / "server"
    if servidor.is_dir():
        if (servidor / "requirements.txt").exists():
            fallas.append("ADR-0006: server/requirements.txt sigue existiendo")
        if not (servidor / "pyproject.toml").exists():
            fallas.append("ADR-0006: falta server/pyproject.toml")
        else:
            for nombre in sorted(dependencias(servidor / "pyproject.toml") & DESCARTADAS):
                fallas.append(f"plataformas/fastapi.md: server/ declara {nombre}, que está descartada")
        if (servidor / "pytest.ini").exists():
            fallas.append("ADR-0006: pytest.ini suelto; la configuración va en pyproject.toml")
        if (servidor / "app").is_dir():
            fallas.append("plataformas/fastapi.md: el paquete va en server/src/app/, no en server/app/")
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
        if "@sveltejs/adapter-static" not in deps:
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/ no usa adapter-static")
        if not (superficie / "uno.config.ts").exists():
            fallas.append(f"plataformas/sveltekit.md: {superficie.name}/ no tiene uno.config.ts")
        fallas.extend(
            comparar(
                superficie / ".prettierrc",
                PLANTILLA / "sveltekit/.prettierrc",
                f"{superficie.name}/.prettierrc",
            )
        )

    # Qt y Flet: cada pieza Python que declare la dependencia que la identifica.
    for pyproject in repo.glob("*/pyproject.toml"):
        pieza = pyproject.parent
        declaradas = dependencias(pyproject)
        for dependencia, (plantilla, canonicos) in CANONICOS_PIEZA.items():
            if dependencia not in declaradas:
                continue
            for rel in canonicos:
                fallas.extend(
                    comparar(pieza / rel, PLANTILLA / plantilla / rel, f"{pieza.name}/{rel.as_posix()}")
                )

    # Flutter: solo para las apps que existan.
    for pubspec in repo.glob("*/pubspec.yaml"):
        app = pubspec.parent
        fallas.extend(
            comparar(
                app / "analysis_options.yaml",
                PLANTILLA / "flutter/analysis_options.yaml",
                f"{app.name}/analysis_options.yaml",
            )
        )

    # Android: solo para las apps que existan.
    for settings in repo.glob("*/settings.gradle.kts"):
        app = settings.parent
        fallas.extend(
            comparar(app / ".editorconfig", PLANTILLA / "android/.editorconfig", f"{app.name}/.editorconfig")
        )

    docs = repo / "docs"
    if docs.is_dir():
        permitidos = {"README.md", "arquitectura", "adr", "planes"}
        sueltos = sorted(p.name for p in docs.iterdir() if p.name not in permitidos)
        if sueltos:
            fallas.append(
                "documentacion.md: docs/ tiene archivos fuera de la convención: "
                + ", ".join(sueltos)
            )

    fallas.extend(nombres_largos(repo))
    fallas.extend(configuracion_con_repositorio(repo))

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
