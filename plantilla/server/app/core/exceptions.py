from dataclasses import dataclass

from app.core.enums import ProblemType


@dataclass(frozen=True)
class Problem:
    title: str
    status: int
    description: str


# ADR-0015: la única fuente de cada tipo. AppError toma de aquí el
# title y el status, y /problems/{slug} sirve la descripción.
PROBLEMS: dict[ProblemType, Problem] = {
    ProblemType.VALIDATION_ERROR: Problem(
        title="Datos inválidos",
        status=422,
        description="La petición no pasó la validación. Cada elemento de errors "
        "señala un campo con un JSON Pointer.",
    ),
}


class AppError(Exception):
    """Error de la aplicación.

    Un handler de main.py lo responde como ProblemDetails.
    """

    def __init__(self, problem_type: ProblemType, detail: str) -> None:
        super().__init__(detail)
        self.type = problem_type
        self.title = PROBLEMS[problem_type].title
        self.status = PROBLEMS[problem_type].status
        self.detail = detail
