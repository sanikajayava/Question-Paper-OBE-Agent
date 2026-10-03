import json
from pathlib import Path


def read_question_bank():
    """
    Tool to read questions from the question bank.
    """

    file_path = Path(__file__).parent.parent / "data" / "question_bank.json"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            questions = json.load(file)

        return {
            "status": "success",
            "count": len(questions),
            "questions": questions
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Question bank file not found."
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Question bank contains invalid JSON."
        }