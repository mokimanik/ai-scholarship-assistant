import json
import ollama
from fastapi import HTTPException

from backend import config
from models.scholarship import Scholarship


def generate_summary(scholarship_id: str) -> str:
    """
    Load scholarship by id, build a prompt asking Ollama to explain
    the scholarship in one plain-English sentence for a student,
    and return the response text.
    """
    if not config.SCHOLARSHIPS_FILE_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Scholarship with ID '{scholarship_id}' not found."
        )

    with open(config.SCHOLARSHIPS_FILE_PATH, "r", encoding="utf-8") as f:
        scholarships_data = json.load(f)

    target_data = next(
        (s for s in scholarships_data if str(s.get("id")).lower() == scholarship_id.lower()),
        None
    )

    if not target_data:
        raise HTTPException(
            status_code=404,
            detail=f"Scholarship with ID '{scholarship_id}' not found."
        )

    scholarship = Scholarship.from_dict(target_data)

    prompt = (
        f"Explain the following scholarship in one plain-English sentence for a student:\n"
        f"Name: {scholarship.name}\n"
        f"Category: {scholarship.category}\n"
        f"Min CGPA: {scholarship.min_cgpa}\n"
        f"Max Family Income: {scholarship.max_family_income}\n"
        f"Eligible Academic Years: {scholarship.eligible_years}\n"
        f"Amount: {scholarship.amount}\n"
        f"Deadline: {scholarship.deadline}\n"
        f"Required Documents: {', '.join(scholarship.required_docs)}"
    )

    response = ollama.generate(
        model="llama3.1",
        prompt=prompt
    )

    return response.get("response", "").strip()
