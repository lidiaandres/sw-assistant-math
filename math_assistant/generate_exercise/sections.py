from __future__ import annotations

from datetime import date, timedelta
from typing import Any

SECTION_TITLES: list[str] = [
    "Identidades y ecuaciones",
    "Elementos de una ecuación",
    "Ecuaciones equivalentes",
    "Ecuaciones de primer grado (sumar/restar)",
    "Ecuaciones de primer grado (multiplicar/dividir)",
    "Ecuaciones de primer grado (combinadas)",
    "Resolución de problemas",
]


SECTION_KEY_BY_TITLE: dict[str, str] = {
    "Identidades y ecuaciones": "identidades_y_ecuaciones",
    "Elementos de una ecuación": "elementos_ecuacion",
    "Ecuaciones equivalentes": "ecuaciones_equivalentes",
    "Ecuaciones de primer grado (sumar/restar)": "primer_grado_sumar_restar",
    "Ecuaciones de primer grado (multiplicar/dividir)": "primer_grado_multiplicar_dividir",
    "Ecuaciones de primer grado (combinadas)": "primer_grado_combinadas",
    "Resolución de problemas": "resolucion_problemas",
}



def next_section_title(current_title: str) -> str:
    if current_title not in SECTION_TITLES:
        return SECTION_TITLES[0]
    idx = SECTION_TITLES.index(current_title)
    return SECTION_TITLES[(idx + 1) % len(SECTION_TITLES)]


def recommended_section_titles(progress: dict[str, Any]) -> tuple[str, str]:

    try:
        total_hechos = sum(
            int((progress.get(SECTION_KEY_BY_TITLE[t]) or {}).get("hechos", 0) or 0)
            for t in SECTION_TITLES
        )
    except Exception:
        total_hechos = 0
    if total_hechos <= 0:
        return SECTION_TITLES[0], SECTION_TITLES[1]

    meta: dict[str, Any] = (progress.get("_meta") or {}) if isinstance(progress, dict) else {}
    last_title_raw = meta.get("last_section")
    last_title = last_title_raw if isinstance(last_title_raw, str) and last_title_raw in SECTION_TITLES else None

    primary = last_title or SECTION_TITLES[0]
    if last_title:
        primary = last_title

    secondary = next_section_title(primary)
    return primary, secondary
