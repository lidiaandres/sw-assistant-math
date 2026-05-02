import streamlit as st
import json
from html import escape
from pathlib import Path

from math_assistant.generate_exercise.sections import (
    SECTION_KEY_BY_TITLE,
    SECTION_TITLES,
    recommended_section_titles,
)
from math_assistant.generate_exercise.identities_equations import (select_exercise as exercise_identities, 
                                                                   check_answer as check_identities)
from math_assistant.generate_exercise.equation_elements import (select_exercise as exercise_elements, 
                                                                check_answer as check_elements)
from math_assistant.generate_exercise.equivalent_equations import (select_exercise as exercise_equivalent, 
                                                                   check_answer as check_equivalent)
from math_assistant.generate_exercise.addition_subtraction_equations import (select_exercise as exercise_add, 
                                                                             check_answer as check_equations_add)
from math_assistant.generate_exercise.multiplication_division_equations import (select_exercise as exercise_mult, 
                                                                                check_answer as check_mult)
from math_assistant.generate_exercise.combined_equations import (select_exercise as exercise_combine,
                                                                 check_answer as check_combine)
from math_assistant.generate_exercise.problem_solving import (select_exercise as problem_equation,
                                                              check_answer as check_problem)




# ---------------------------------------------------
# Configuración general de la app
# ---------------------------------------------------
st.set_page_config(
    page_title="Descubriendo las matemáticas — 1º ESO",
    page_icon="✨",
    layout="centered",
)


st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
  html, body, .stApp, [data-testid="stMarkdownContainer"] p {
    font-family: "Poppins", sans-serif;
  }
  /* Fondo azul clarito en toda la interfaz */
  html, body {
    background-color: #e3f2fd;
  }
  section[data-testid="stMain"] > div {
    background-color: #e3f2fd !important;
  }
  [data-testid="stAppViewContainer"] > .main {
    background-color: #e3f2fd;
  }
  .stApp {
    background-color: #e3f2fd;
  }
  /* Cabecera: bloque azul oscuro */
  .brand-top {
    background: #081A41;
    color: #FFFFFF;
    border-radius: 20px;
    padding: 1.15rem 1.25rem 1.05rem;
    text-align: center;
    margin: 0 0 1.1rem 0;
    box-shadow: 0 8px 20px rgba(14, 100, 161, 0.35);
    line-height: 1.2;
  }
  .brand-top .brand-title {
    margin: 0;
    font-size: clamp(1.25rem, 3.8vw, 1.85rem);
    font-weight: 1000;
    letter-spacing: 0.02em;
  }
  .brand-top .brand-course {
    margin: 0.55rem 0 0;
    font-size: clamp(0.95rem, 2.6vw, 1.1rem);
    font-weight: 600;
    opacity: 0.93;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
</style>
<div class="brand-top">
  <div class="brand-title">Descubriendo las matemáticas</div>
  <div class="brand-course">1º ESO</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

PROGRESS_FILE: Path = Path(__file__).with_name("progress.json")
GOAL_TOTAL_EXERCISES: int = 20


def _pretty_equation_html(equation: str) -> str:
    safe = escape(str(equation))
    return (
        "<b><span style=\"font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "
        "'Liberation Mono', 'Courier New', monospace; color: #000;\">"
        f"{safe}"
        "</span></b>"
    )


def _load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {
            **{
                SECTION_KEY_BY_TITLE[title]: {"hechos": 0, "aciertos": 0}
                for title in SECTION_TITLES
            }
        }
    try:
        raw = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "sections" in raw and isinstance(raw.get("sections"), dict):
            raw = {**raw["sections"]}
        for title in SECTION_TITLES:
            key = SECTION_KEY_BY_TITLE[title]
            raw.setdefault(key, {"hechos": 0, "aciertos": 0})

        allowed_keys: set[str] = {SECTION_KEY_BY_TITLE[t] for t in SECTION_TITLES} | {
            "_meta",
        }
        raw = {k: v for (k, v) in raw.items() if k in allowed_keys}
        return raw
    except Exception:
        return {
            **{
                SECTION_KEY_BY_TITLE[title]: {"hechos": 0, "aciertos": 0}
                for title in SECTION_TITLES
            }
        }


def _save_progress(progress: dict) -> None:
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _progress_bar(pct: int, width: int = 10) -> str:
    pct = max(0, min(100, pct))
    filled = round((pct / 100) * width)
    return ("█" * filled) + ("░" * (width - filled))


def _compute_overall_progress(progress: dict) -> tuple[int, int, int]:
    section_keys: list[str] = [SECTION_KEY_BY_TITLE[t] for t in SECTION_TITLES]
    total_hechos = sum(int((progress.get(k) or {}).get("hechos", 0)) for k in section_keys)
    total_aciertos = sum(int((progress.get(k) or {}).get("aciertos", 0)) for k in section_keys)
    pct = int(min(100, round((total_hechos / GOAL_TOTAL_EXERCISES) * 100))) if GOAL_TOTAL_EXERCISES > 0 else 0
    return pct


def _render_home_panel(progress: dict) -> None:
    pct = _compute_overall_progress(progress)
    meta: dict = progress.get("_meta", {}) if isinstance(progress, dict) else {}

    st.markdown(
        f"""
<div style="font-family: 'Poppins', sans-serif;">
  <div style="font-size: 1rem; line-height: 1.25; margin-bottom: 0.65rem;">
    📊 <b>Progreso en la unidad de ecuaciones:</b>
    <span style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;">
      {_progress_bar(pct)}
    </span>
    <b>{pct}%</b>
  </div>
</div>
""".strip(),
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        f"""
<div style="font-family: 'Poppins', sans-serif;">
¡Bienvenido/a! 👋 Soy tu asistente de 'Ecuaciones'. \n
Vamos a resolverlas paso a paso.
</div>
""".strip(),
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("👉 CONTINUAR", use_container_width=True):
            last_title = meta.get("last_section")
            if isinstance(last_title, str) and last_title in SECTION_TITLES:
                st.session_state.pending_section = last_title
                st.rerun()
            st.info("Aún no has empezado ningún apartado. Elige uno en 📚 **ELEGIR TIPO DE EJERCICIO**.")
        st.caption("Sigue donde lo dejaste")

    with col_b:
        if st.button("📚 ELEGIR TIPO DE EJERCICIO", use_container_width=True):
            st.session_state.view = "choose_type"
            st.rerun()
        st.caption("Ver apartados")


def _render_choose_type_view() -> None:
    progress = _load_progress()
    primary_title, secondary_title = recommended_section_titles(progress)

    st.markdown(
        """
<div style="font-family: 'Poppins', sans-serif;">
  <div style="font-size: 1.35rem; font-weight: 800; margin-bottom: 0.65rem;">
    Recomendados para ti
  </div>
</div>
""".strip(),
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")

    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button(f"⭐ {primary_title}", use_container_width=True):
            st.session_state.pending_section = primary_title
            st.session_state.view = "chat"
            st.rerun()
    with col_b:
        if st.button(f"⚠️ {secondary_title}", use_container_width=True):
            st.session_state.pending_section = secondary_title
            st.session_state.view = "chat"
            st.rerun()
    
    if st.button(f"📝 Repaso de cualquier apartado", width = 345):
        st.session_state.view = "repaso"
        st.rerun()

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    if st.button("🏠 Volver al inicio", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()


def _has_user_message(messages: list[dict[str, str]]) -> bool:
    return any(m.get("role") == "user" for m in messages)


def _append_section_exchange(section_title: str) -> None:

    progress = _load_progress()
    meta: dict = progress.setdefault("_meta", {})
    meta["last_section"] = section_title
    st.session_state.current_section_title = section_title
    st.session_state.can_next = False

    key = SECTION_KEY_BY_TITLE.get(section_title)

    if isinstance(key, str):
        st.session_state.last_section_key = key

    match section_title:
        case "Identidades y ecuaciones":
            exercise, num_exercise = exercise_identities(progress)
        case "Elementos de una ecuación":
            exercise, state = exercise_elements(progress)
            st.session_state.elements_state = state
            num_exercise = 0
        case "Ecuaciones equivalentes":
            exercise, state = exercise_equivalent(progress)
            st.session_state.equivalent_state = state
            num_exercise = 0
        case "Ecuaciones de primer grado (sumar/restar)":
            exercise, num_exercise = exercise_add(progress)
        case "Ecuaciones de primer grado (multiplicar/dividir)":
            exercise, num_exercise = exercise_mult(progress)
        case "Ecuaciones de primer grado (combinadas)":
            exercise, num_exercise = exercise_combine(progress)
        case "Resolución de problemas":
            exercise, num_exercise = problem_equation(progress)
        case _:
            exercise, num_exercise = "No se encontró el ejercicio relacionado con el apartado seleccionado", ""

    last_shown = st.session_state.get("last_shown_section_title")
    if not isinstance(last_shown, str) or last_shown != section_title:
        st.session_state.messages.append({"role": "assistant", "content": f"📌 **{section_title}**"})
        st.session_state.last_shown_section_title = section_title

    secciones_seleccionadas = {'Identidades y ecuaciones', 
                               'Ecuaciones de primer grado (sumar/restar)', 
                               'Ecuaciones de primer grado (multiplicar/dividir)', 
                               'Ecuaciones de primer grado (combinadas)'} 
    st.session_state.messages.append(
    {
        "role": "assistant",
        "content": (
            f"Resuelve el siguiente ejercicio y escribe tu resultado:\n\n"
            f"<b>{_pretty_equation_html(exercise) if section_title in secciones_seleccionadas else exercise}</b>"
        ),
    })

    try:
        st.session_state.current_exercise_id = int(num_exercise)
    except Exception:
        st.session_state.current_exercise_id = 1
    st.session_state.awaiting_answer = True
    st.session_state.last_check_ok = None


# ---------------------------------------------------
# Estado de la conversación
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "¡Comenzamos!"
            ),
        }
    ]

if "pending_section" not in st.session_state:
    st.session_state.pending_section = None

if "last_section_key" not in st.session_state:
    st.session_state.last_section_key = None

if "current_section_title" not in st.session_state:
    st.session_state.current_section_title = None

if "current_exercise_id" not in st.session_state:
    st.session_state.current_exercise_id = 1

if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False

if "last_check_ok" not in st.session_state:
    st.session_state.last_check_ok = None

if "can_next" not in st.session_state:
    st.session_state.can_next = False

if "last_shown_section_title" not in st.session_state:
    st.session_state.last_shown_section_title = None

if "elements_state" not in st.session_state:
    st.session_state.elements_state = None

if "equivalent_state" not in st.session_state:
    st.session_state.equivalent_state = None

if "pending_part" not in st.session_state:
    st.session_state.pending_part = None

if "view" not in st.session_state:
    st.session_state.view = "home"

if st.session_state.pending_section:
    title = st.session_state.pending_section
    st.session_state.pending_section = None
    _append_section_exchange(title)
    st.session_state.view = "chat"

if user_text := st.chat_input("Escribe tu respuesta aquí…"):
    st.session_state.messages.append({"role": "user", "content": user_text})

    if st.session_state.get("awaiting_answer", False):

        progress = _load_progress()

        if st.session_state.get("current_section_title") == "Identidades y ecuaciones":

            print(progress["identidades_y_ecuaciones"]["hechos"])

            progress.setdefault("identidades_y_ecuaciones", {"hechos": 0, "aciertos": 0})
            progress["identidades_y_ecuaciones"].setdefault("totales", 4)

            feedback = check_identities(user_text.strip(), int(st.session_state.current_exercise_id))
            progress["identidades_y_ecuaciones"]["hechos"] = int(progress["identidades_y_ecuaciones"].get("hechos", 0) or 0) + 1
            _save_progress(progress)
            progress["identidades_y_ecuaciones"]["hechos"]

            st.session_state.messages.append({"role": "assistant", "content": feedback})
            ok = feedback.startswith("¡Muy bien!")
            st.session_state.last_check_ok = ok
            st.session_state.awaiting_answer = False
            st.session_state.can_next = True

            st.rerun()

        elif st.session_state.get("current_section_title") == "Elementos de una ecuación":
            
            state = st.session_state.get("elements_state") or {"exercise_idx": 0, "part_idx": 0}

            feedback, finished_exercise, finished_section = check_elements(
                progress, user_text.strip(), state
            )
            _save_progress(progress)

            st.session_state.messages.append({"role": "assistant", "content": feedback})

            if finished_section:
                st.session_state.awaiting_answer = False
                st.session_state.can_next = True
            elif finished_exercise:
                st.session_state.awaiting_answer = False
                st.session_state.can_next = True
            else:
                next_prompt, next_state = exercise_elements(progress)
                st.session_state.pending_part = {
                    "section": "Elementos de una ecuación",
                    "prompt": str(next_prompt),
                    "state": next_state,
                }
                st.session_state.awaiting_answer = False
                st.session_state.can_next = False

            st.rerun()

        elif st.session_state.get("current_section_title") == "Ecuaciones equivalentes":

            state = st.session_state.get("equivalent_state") or {"exercise_idx": 0, "part_idx": 0}

            feedback, finished_exercise, finished_section = check_equivalent(
                progress, user_text.strip(), state
            )
            _save_progress(progress)

            st.session_state.messages.append({"role": "assistant", "content": feedback})

            if finished_section:
                st.session_state.awaiting_answer = False
                st.session_state.can_next = True
            elif finished_exercise:
                st.session_state.awaiting_answer = False
                st.session_state.can_next = True
            else:
                next_prompt, next_state = exercise_equivalent(progress)
                st.session_state.pending_part = {
                    "section": "Ecuaciones equivalentes",
                    "prompt": str(next_prompt),
                    "state": next_state,
                }
                st.session_state.awaiting_answer = False
                st.session_state.can_next = False

            st.rerun()

        elif st.session_state.get("current_section_title") == "Ecuaciones de primer grado (sumar/restar)":

            progress.setdefault("primer_grado_sumar_restar", {"hechos": 0, "aciertos": 0})
            progress["primer_grado_sumar_restar"].setdefault("totales", 3)

            feedback = check_equations_add(user_text.strip(), int(st.session_state.current_exercise_id))
            progress["primer_grado_sumar_restar"]["hechos"] = int(progress["primer_grado_sumar_restar"].get("hechos", 0) or 0) + 1
            _save_progress(progress)

            st.session_state.messages.append({"role": "assistant", "content": feedback})
            ok = feedback.startswith("¡Muy bien!")
            st.session_state.last_check_ok = ok
            st.session_state.awaiting_answer = False
            st.session_state.can_next = True
            st.rerun()

        elif st.session_state.get("current_section_title") == "Ecuaciones de primer grado (multiplicar/dividir)":

            progress.setdefault("primer_grado_multiplicar_dividir", {"hechos": 0, "aciertos": 0})
            progress["primer_grado_multiplicar_dividir"].setdefault("totales", 3)

            feedback = check_mult(user_text.strip(), int(st.session_state.current_exercise_id))
            progress["primer_grado_multiplicar_dividir"]["hechos"] = int(progress["primer_grado_multiplicar_dividir"].get("hechos", 0) or 0) + 1
            _save_progress(progress)

            st.session_state.messages.append({"role": "assistant", "content": feedback})
            ok = feedback.startswith("¡Muy bien!")
            st.session_state.last_check_ok = ok
            st.session_state.awaiting_answer = False
            st.session_state.can_next = True
            st.rerun()

        elif st.session_state.get("current_section_title") == "Ecuaciones de primer grado (combinadas)":

            progress.setdefault("primer_grado_combinadas", {"hechos": 0, "aciertos": 0})
            progress["primer_grado_combinadas"].setdefault("totales", 3)

            feedback = check_combine(user_text.strip(), int(st.session_state.current_exercise_id))
            progress["primer_grado_combinadas"]["hechos"] = int(progress["primer_grado_combinadas"].get("hechos", 0) or 0) + 1
            _save_progress(progress)

            st.session_state.messages.append({"role": "assistant", "content": feedback})
            ok = feedback.startswith("¡Muy bien!")
            st.session_state.last_check_ok = ok
            st.session_state.awaiting_answer = False
            st.session_state.can_next = True
            st.rerun()

        elif st.session_state.get("current_section_title") == "Resolución de problemas":

            progress.setdefault("resolucion_problemas", {"hechos": 0, "aciertos": 0})
            progress["resolucion_problemas"].setdefault("totales", 3)

            feedback = check_problem(user_text.strip(), int(st.session_state.current_exercise_id))
            progress["resolucion_problemas"]["hechos"] = int(progress["resolucion_problemas"].get("hechos", 0) or 0) + 1
            _save_progress(progress)

            st.session_state.messages.append({"role": "assistant", "content": feedback})
            ok = feedback.startswith("¡Muy bien!")
            st.session_state.last_check_ok = ok
            st.session_state.awaiting_answer = False
            st.session_state.can_next = True
            st.rerun()

    else:
        _append_section_exchange(user_text)
        st.session_state.view = "chat"

if st.session_state.view == "choose_type":
    _render_choose_type_view()
elif st.session_state.view == "home" and not _has_user_message(st.session_state.messages):
    _render_home_panel(_load_progress())
elif st.session_state.view == "repaso":

    prog = _load_progress()
    seccion_actual = prog["_meta"]["last_section"]
    posicion_seccion = SECTION_TITLES.index(seccion_actual)

    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button(f"{SECTION_TITLES[0]}", use_container_width=True):
            st.session_state.pending_section = SECTION_TITLES[0]
            st.session_state.view = "chat"
            st.rerun()
        if posicion_seccion == 0:
            st.caption("Te encuentras en este apartado")
    
    with col_b:
        if st.button(f"{SECTION_TITLES[1]}", use_container_width=True):
            st.session_state.pending_section = SECTION_TITLES[1]
            st.session_state.view = "chat"
            st.rerun()
        if posicion_seccion == 1:
            st.caption("Te encuentras en este apartado")
    
    st.write("")
    st.write("")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button(f"{SECTION_TITLES[2]}", use_container_width=True):
            st.session_state.pending_section = SECTION_TITLES[2]
            st.session_state.view = "chat"
            st.rerun()
        if posicion_seccion == 2:
            st.caption("Te encuentras en este apartado")
    
    with col_b:
        if st.button(f"{SECTION_TITLES[3]}", use_container_width=True):
            st.session_state.pending_section = SECTION_TITLES[3]
            st.session_state.view = "chat"
            st.rerun()
        if posicion_seccion == 3:
            st.caption("Te encuentras en este apartado")
    
    st.write("")
    st.write("")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button(f"{SECTION_TITLES[4]}", use_container_width=True):
            st.session_state.pending_section = SECTION_TITLES[4]
            st.session_state.view = "chat"
            st.rerun()
        if posicion_seccion == 4:
            st.caption("Te encuentras en este apartado")
    
    with col_b:
        if st.button(f"{SECTION_TITLES[5]}", use_container_width=True):
            st.session_state.pending_section = SECTION_TITLES[5]
            st.session_state.view = "chat"
            st.rerun()
        if posicion_seccion == 5:
            st.caption("Te encuentras en este apartado")
    
    st.write("")
    st.write("")
    if st.button(f"{SECTION_TITLES[6]}", width = 345):
        st.session_state.pending_section = SECTION_TITLES[6]
        st.session_state.view = "chat"
        st.rerun()
    if posicion_seccion == 6:
            st.caption("Te encuentras en este apartado")

else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    pending_part = st.session_state.get("pending_part")
    if isinstance(pending_part, dict) and pending_part.get("prompt") and not st.session_state.get("awaiting_answer", False):
        if st.button("▶️ Continuar", use_container_width=True):
            prompt = str(pending_part.get("prompt", ""))
            section = str(pending_part.get("section", ""))
            state = pending_part.get("state")
            if section == "Elementos de una ecuación":
                st.session_state.elements_state = state
            elif section == "Ecuaciones equivalentes":
                st.session_state.equivalent_state = state
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Siguiente parte:\n\n<b>{prompt}</b>",
                }
            )
            st.session_state.pending_part = None
            st.session_state.awaiting_answer = True
            st.session_state.can_next = False
            st.rerun()

    if st.session_state.get("can_next", False):
        progress = _load_progress()

        section_title = st.session_state.get("current_section_title")
        section_key = SECTION_KEY_BY_TITLE.get(section_title) if isinstance(section_title, str) else None

        if isinstance(section_key, str):
            block = progress.get(section_key, {})
            hechos = int(block.get("hechos", 0) or 0)
            totales = int(block.get("totales", 0) or 0)
            finished = totales > 0 and hechos >= totales
        else:
            finished = False

        if not finished:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("➡️ Siguiente ejercicio", use_container_width=True):
                    st.session_state.can_next = False
                    st.session_state.pending_section = section_title
                    st.session_state.view = "chat"
                    st.rerun()
            with col_b:
                if st.button("🏠 Volver al inicio", use_container_width=True):
                    st.session_state.messages = [
                        {
                            "role": "assistant",
                            "content": "¡Comenzamos!",
                        }
                    ]
                    st.session_state.pending_section = None
                    st.session_state.last_section_key = None
                    st.session_state.current_section_title = None
                    st.session_state.current_exercise_id = 1
                    st.session_state.awaiting_answer = False
                    st.session_state.last_check_ok = None
                    st.session_state.can_next = False
                    st.session_state.last_shown_section_title = None
                    st.session_state.elements_state = None
                    st.session_state.equivalent_state = None
                    st.session_state.view = "home"
                    st.rerun()
        else:
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("⏭️ Siguiente apartado", use_container_width=True):

                    progress = _load_progress()
                    if isinstance(section_key, str):
                        progress.setdefault(section_key, {})
                        progress[section_key]["hechos"] = 0
                        if "part" in progress[section_key]:
                            progress[section_key]["part"] = 0
                        _save_progress(progress)

                    if isinstance(section_title, str) and section_title in SECTION_TITLES:
                        idx = SECTION_TITLES.index(section_title)
                        next_title = SECTION_TITLES[(idx + 1) % len(SECTION_TITLES)]
                    else:
                        next_title = SECTION_TITLES[0]

                    st.session_state.can_next = False
                    st.session_state.awaiting_answer = False
                    st.session_state.last_check_ok = None

                    st.session_state.elements_state = None
                    st.session_state.equivalent_state = None
                    st.session_state.pending_section = next_title
                    st.session_state.view = "chat"
                    st.rerun()
            
            with col_b:
                if st.button("🔁 Repetir el apartado", use_container_width=True):

                    progress = _load_progress()
                    if isinstance(section_key, str):
                        progress.setdefault(section_key, {})
                        progress[section_key]["hechos"] = 0
                        progress[section_key]["aciertos"] = 0

                        if "part" in progress[section_key]:
                            progress[section_key]["part"] = 0
                    _save_progress(progress)

                    st.session_state.can_next = False
                    if section_key == "elementos_ecuacion":
                        st.session_state.elements_state = {"exercise_idx": 0, "part_idx": 0}
                    if section_key == "ecuaciones_equivalentes":
                        st.session_state.equivalent_state = {"exercise_idx": 0, "part_idx": 0}
                    st.session_state.pending_section = section_title
                    st.session_state.view = "chat"
                    st.rerun()

            with col_c:
                if st.button("🏠 Volver al inicio", use_container_width=True):

                    progress = _load_progress()
                    if isinstance(section_key, str):
                        progress.setdefault(section_key, {})
                        progress[section_key]["hechos"] = 0
                        if "part" in progress[section_key]:
                            progress[section_key]["part"] = 0
                        _save_progress(progress)

                    st.session_state.messages = [
                        {
                            "role": "assistant",
                            "content": "¡Comenzamos!",
                        }
                    ]
                    st.session_state.pending_section = None
                    st.session_state.last_section_key = None
                    st.session_state.current_section_title = None
                    st.session_state.current_exercise_id = 1
                    st.session_state.awaiting_answer = False
                    st.session_state.last_check_ok = None
                    st.session_state.can_next = False
                    st.session_state.last_shown_section_title = None
                    st.session_state.elements_state = None
                    st.session_state.equivalent_state = None
                    st.session_state.view = "home"
                    st.rerun()
