import json
from fastapi import HTTPException

from backend import config
from models.scholarship import Scholarship
from backend.data_loader import load_scholarships
from backend.chains.summary_chain import generate_scholarship_summary


def generate_summary(scholarship_id: str) -> str:
    """
    Load scholarship by id, build a prompt asking Gemini API to explain
    the scholarship in one plain-English sentence for a student,
    and return the response text.
    """
    scholarships = load_scholarships()
    scholarship = next(
        (s for s in scholarships if s.id.lower() == scholarship_id.lower()),
        None
    )

    if not scholarship:
        raise HTTPException(
            status_code=404,
            detail=f"Scholarship with ID '{scholarship_id}' not found."
        )

    return generate_scholarship_summary(scholarship)
