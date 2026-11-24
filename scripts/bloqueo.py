"""Escribe la lista de bloqueo de la plantilla del servidor desde la lista del NCSC de fuentes/.

    python scripts/bloqueo.py
"""

from verificar import BLOQUEO, lista_de_bloqueo


def main() -> None:
    BLOQUEO.write_text(lista_de_bloqueo(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
