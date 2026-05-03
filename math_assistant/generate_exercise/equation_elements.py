from __future__ import annotations

from typing import Any
from html import escape

from math_assistant.generate_exercise.list_exercises import _EXERCISES


SECTION_KEY: str = "elementos_ecuacion"


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
    part_name = parts[part_idx]

    prompt = (
        f"Esta es la ecuación:\n\n"
        f"<b><span style=\"font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; color: #000;\">{escape(equation)}</span></b>\n\n"
        f"Identifica sus elementos. {part_name}:"
    )
    state = {"exercise_idx": ex_idx, "part_idx": part_idx}
    return prompt, state


def check_answer(progress: dict[str, Any], answer: str, state: dict[str, int]) -> tuple[str, bool, bool]:

    block = progress.setdefault(SECTION_KEY, {"hechos": 0, "aciertos": 0, "totales": 3, "part": 0})
    data = _EXERCISES[SECTION_KEY]
    parts: list[str] = list(data["parts"])

    ex_idx = int(state.get("exercise_idx", int(block.get("hechos", 0) or 0)))
    part_idx = int(state.get("part_idx", int(block.get("part", 0) or 0)))
    ex_idx = max(0, min(ex_idx, len(data["exercises"]) - 1))
    part_idx = max(0, min(part_idx, len(parts) - 1))

    exercise = data["exercises"][str(ex_idx)]
    part_name = parts[part_idx]
    expected = str(exercise["solutions"].get(part_name, "")).strip()
    given = str(answer).strip()

    ok = given.lower().replace(" ", "") == expected.lower().replace(" ", "")
    if ok:
        feedback = "¡Muy bien! Sigue así. 🌟"
    else:
        feedback = f"❌ No es correcto. La respuesta era: **{expected}**.\n\n Buen intento, vamos con el siguiente ejercicio. 💪"

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
