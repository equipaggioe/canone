from html import escape

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.core.enums import ProblemType
from app.core.exceptions import PROBLEMS

# ADR-0015: el type de un error apunta aquí, y el RFC 9457 pide que
# al abrirlo haya documentación legible. Se monta sin prefijo: el type
# no cambia entre versiones de la API.
router = APIRouter(include_in_schema=False)


@router.get("/problems/{slug}", response_class=HTMLResponse)
async def read_problem(slug: str) -> str:
    try:
        problem = PROBLEMS[ProblemType(f"/problems/{slug}")]
    except ValueError:
        raise HTTPException(status_code=404) from None
    title = escape(problem.title)
    return (
        f'<!doctype html><html lang="es"><meta charset="utf-8"><title>{title}</title>'
        f"<h1>{title}</h1><p>Código HTTP {problem.status}.</p>"
        f"<p>{escape(problem.description)}</p></html>"
    )
