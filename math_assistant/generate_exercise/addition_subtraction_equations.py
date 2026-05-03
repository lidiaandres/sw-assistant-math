from math_assistant.generate_exercise.list_exercises import _EXERCISES


SECTION_KEY: str = "primer_grado_sumar_restar"

def check_answer(answer: str, num_exercise: int) -> str:

    print(f"answer: {answer}, num_exercise: {num_exercise}")
    solutions = _EXERCISES[SECTION_KEY]["solutions"]
    expected = solutions.get(str(num_exercise), {}).get("solution")
    explanation = solutions.get(str(num_exercise), {}).get("explanation", "")
    if expected is not None and answer.lower().replace(" ", "") == str(expected).lower().replace(" ", ""):
        return "¡Muy bien! Sigue así. 🌟"
    return f"❌ No es correcto.\n\n{explanation}\n\n. Buen intento, vamos con el siguiente ejercicio. 💪"

def select_exercise(progress: dict) -> tuple[str, int]:

    block = progress.get(SECTION_KEY, {})
    done = block.get("hechos", 0)
    total = block.get("totales", 0)

    if done >= total:
        done = 0

    exercises = _EXERCISES[SECTION_KEY]["exercises"]
    return exercises.get(str(done), ""), done

