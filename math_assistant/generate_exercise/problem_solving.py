import re

from math_assistant.generate_exercise.list_exercises import _EXERCISES

SECTION_KEY: str = "resolucion_problemas"

def extract_numbers(text):

    text = text.replace("\n", " ")
    patron = r"(?<![a-zA-ZáéíóúÁÉÍÓÚñÑ])-?\d+(?:[.,]\d+)?"
    numbers = re.findall(patron, text)

    return [float(n.replace(",", ".")) for n in numbers]

def respuesta_correcta(answer, solution, tol=1e-6):
    nums_alumno = extract_numbers(answer)
    nums_solucion = extract_numbers(solution)
    
    if len(nums_alumno) != len(nums_solucion):
        return False
    
    nums_alumno = sorted(nums_alumno)
    nums_solucion = sorted(nums_solucion)

    for a, b in zip(nums_alumno, nums_solucion):
        if abs(a - b) > tol:
            return False
    
    return True

def check_answer(answer: str, num_exercise: int) -> str:
    """Comprueba si la respuesta es correcta."""
    print(f"answer: {answer}, num_exercise: {num_exercise}")
    solutions = _EXERCISES[SECTION_KEY]["solutions"]
    expected = solutions.get(str(num_exercise), {}).get("solution")
    explanation = solutions.get(str(num_exercise), {}).get("explanation", "")
    bool_respuesta = respuesta_correcta(answer, expected)
    if expected is not None and bool_respuesta:
        return "¡Muy bien! Sigue así. 🌟"
    return f"❌ No es correcto.\n\n{explanation}\n\nSigue intentándolo. 💪"

def select_exercise(progress: dict) -> tuple[str, int]:
    """Devuelve el ejercicio de resolución de problemas según el progreso."""
    block = progress.get(SECTION_KEY, {})
    done = block.get("hechos", 0)
    total = block.get("totales", 0)

    if done >= total:
        done = 0

    exercises = _EXERCISES[SECTION_KEY]["exercises"]
    return exercises.get(str(done), ""), done

