from math_assistant.generate_exercise.list_exercises import _EXERCISES

SECTION_KEY: str = "identidades_y_ecuaciones"

def check_answer(answer: str, num_exercise: int) -> str:

    solutions = _EXERCISES[SECTION_KEY]["solutions"]
    expected = solutions.get(str(num_exercise), {}).get("solution")
    explanation = solutions.get(str(num_exercise), {}).get("explanation", "")
    if expected is not None and answer == str(expected):
        return "¡Muy bien! Sigue así. 🌟"
    return f"❌ No es correcto.\n\n{explanation}\n\nSigue intentándolo. 💪"

def select_exercise(progress: dict) -> tuple[str, int]:

    block = progress.get(SECTION_KEY, {})
    done = block.get("hechos", 0)
    total = block.get("totales", 0)

    print(f"done: {done}, total: {total}")

    if done >= total:
        done = 0
    
    change_section = SECTION_KEY.lower().replace(" ", "_")

    exercises = _EXERCISES[change_section]["exercises"]
    return exercises.get(str(done), ""), done

