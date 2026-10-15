"""Export the OpenAPI of the app to openapi.json."""

import json
from pathlib import Path

from app.main import app

FILE = Path(__file__).parents[2] / "openapi.json"


def render() -> str:
    """Return the OpenAPI as the text of openapi.json."""
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    FILE.write_text(render(), encoding="utf-8")
