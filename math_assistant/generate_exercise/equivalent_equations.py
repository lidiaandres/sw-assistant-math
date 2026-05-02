from __future__ import annotations

from typing import Any
from html import escape

from sympy import Eq, S, simplify, solveset
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    standard_transformations,
    parse_expr,
)

from math_assistant.generate_exercise.list_exercises import _EXERCISES


SECTION_KEY: str = "ecuaciones_equivalentes"


def select_exercise(progress: dict[str, Any]) -> tuple[str, dict[str, int]]:

    block = progress.setdefault(SECTION_KEY, {"hechos": 0, "aciertos": 0, "totales": 3, "part": 0})
    try:
        ex_idx = int(block.get("hechos", 0))
    except Exception:
        ex_idx = 0
    try:
        part_idx = int(block.get("part", 0))
    except Exception:
        part_idx = 0

    data = _EXERCISES[SECTION_KEY]
    parts: list[str] = list(data["parts"])
    ex_idx = max(0, min(ex_idx, len(data["exercises"]) - 1))
    part_idx = max(0, min(part_idx, len(parts) - 1))

    exercise = data["exercises"][str(ex_idx)]
    equation = str(exercise["equation"])
    part_name = parts[part_idx].lower()

    prompt = (
        f"Esta es la ecuación:\n\n"
        f"<b><span style=\"font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; color: #000;\">{escape(equation)}</span></b>\n\n"
        f"Busca una {part_name}:"
    )
    state = {"exercise_idx": ex_idx, "part_idx": part_idx}
    return prompt, state


def ecuaciones_equivalentes(eq1_str: str, eq2_str: str) -> bool:

    transformations = standard_transformations + (implicit_multiplication_application,)

    def _parse_lado(expr: str) -> Any:
        cleaned = str(expr).strip().replace("^", "**")
        return parse_expr(cleaned, transformations=transformations)

    def parse_ecuacion(eq: str) -> Any:
        izquierda, derecha = str(eq).split("=", 1)
        return _parse_lado(izquierda) - _parse_lado(derecha)

    expr1 = parse_ecuacion(eq1_str)
    expr2 = parse_ecuacion(eq2_str)

    symbols = sorted(set(expr1.free_symbols) | set(expr2.free_symbols), key=lambda s: str(s))
    if len(symbols) == 1:
        x = symbols[0]
        sol1 = solveset(Eq(expr1, 0), x, domain=S.Reals)
        sol2 = solveset(Eq(expr2, 0), x, domain=S.Reals)
        return bool(sol1 == sol2)

    try:
        ratio = simplify(expr1 / expr2)
        return bool(ratio.free_symbols == set() and ratio != 0)
    except Exception:
        return False


def check_answer(progress: dict[str, Any], answer: str, state: dict[str, int]) -> tuple[str, bool, bool]:
    
    block = progress.setdefault(SECTION_KEY, {"hechos": 0, "aciertos": 0, "totales": 3, "part": 0})
    data = _EXERCISES[SECTION_KEY]
    parts: list[str] = list(data["parts"])

    ex_idx = int(state.get("exercise_idx", int(block.get("hechos", 0) or 0)))
    part_idx = int(state.get("part_idx", int(block.get("part", 0) or 0)))
    ex_idx = max(0, min(ex_idx, len(data["exercises"]) - 1))
    part_idx = max(0, min(part_idx, len(parts) - 1))

    exercise = data["exercises"][str(ex_idx)]
    equation = str(exercise["equation"])
    given = str(answer).strip()

    if parts[part_idx] == "Solución":
        expected = str(exercise.get("solutions", {}).get("Solución", "")).strip()
        ok = given.lower().replace(" ", "") == expected.lower().replace(" ", "")
    else:
        
        if "=" not in given:
            feedback = (
                "⚠️ Tu respuesta no tiene el formato adecuado.\n\n"
                "En esta parte debes escribir una **ecuación** que incluya el símbolo `=`.\n\n"
                "Vuelve a intentarlo."
            )
            return feedback, False, False

        ok = ecuaciones_equivalentes(equation, given)
        expected = str(exercise.get("solutions", {}).get("Ecuación equivalente", "")).strip()

    if ok:
        feedback = "¡Muy bien! Sigue así. 🌟"
    else:
        if parts[part_idx] == "Ecuación equivalente":
            feedback = f"❌ No es correcto. \n\n <b>Ten en cuenta que dos ecuaciones son equivalentes cuando tienen la misma solución.<b>\n\n <b>Una solución posible es: {expected}<b> \n\n Sigue intentándolo. 💪"
        else:
            feedback = f"❌ No es correcto. La respuesta era: **{expected}**.\n\nSigue intentándolo. 💪"

    next_part = part_idx + 1
    finished_exercise = False
    finished_section = False

    if next_part >= len(parts):
        finished_exercise = True
        next_part = 0
        block["hechos"] = int(block.get("hechos", 0) or 0) + 1
        block["part"] = 0
        if int(block.get("hechos", 0) or 0) >= int(block.get("totales", 3) or 3):
            finished_section = True
    else:
        block["part"] = next_part

    block["part"] = int(block.get("part", 0) or 0)

    return feedback, finished_exercise, finished_section
