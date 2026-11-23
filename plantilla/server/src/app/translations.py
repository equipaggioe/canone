"""The texts of the pages the server shows, in the language asked."""

import gettext
from pathlib import Path

from babel.core import negotiate_locale

LOCALES = Path(__file__).parent / "locale"
# transversal.md: the base language.
BASE = "es"


def languages(header: str) -> list[str]:
    """Read Accept-Language, from the most preferred."""
    ranked: list[tuple[float, int, str]] = []
    for position, part in enumerate(header.split(",")):
        tag, _, rest = part.strip().partition(";")
        name, _, value = rest.strip().partition("=")
        try:
            quality = float(value) if name.strip() == "q" else 1.0
        except ValueError:
            continue
        if tag and tag != "*" and quality > 0:
            ranked.append((-quality, position, tag))
    return [tag for _, _, tag in sorted(ranked)]


def translation(header: str) -> gettext.GNUTranslations:
    """Load the catalog of the language asked, or of the base.

    A catalog that was not compiled fails: release.yml compiles them.
    """
    available = sorted(path.name for path in LOCALES.iterdir() if path.is_dir())
    chosen = negotiate_locale(languages(header), available, sep="-") or BASE
    return gettext.translation("messages", LOCALES, languages=[chosen])
