import json
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException

from models.student import Student
from models.scholarship import Scholarship
from backend import config
from backend.ai_client import generate_summary
from backend.rag.qa_chain import answer_policy_question
from backend.graph.workflow import run_scholarship_workflow

app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION
)


def load_students() -> List[Student]:
    """Helper function to load student objects from data/students.json."""
    if not config.STUDENTS_FILE_PATH.exists():
        return []
    with open(config.STUDENTS_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Student.from_dict(item) for item in data]


def load_scholarships() -> List[Scholarship]:
    """Helper function to load scholarship objects from data/scholarships.json."""
    if not config.SCHOLARSHIPS_FILE_PATH.exists():
        return []
    with open(config.SCHOLARSHIPS_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Scholarship.from_dict(item) for item in data]


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint returning server status."""
    return {"status": "ok"}


@app.get("/students")
def get_students() -> List[Dict[str, Any]]:
    """Fetch and return all student records."""
    students = load_students()
    return [student.to_dict() for student in students]


@app.get("/scholarships")
def get_scholarships() -> List[Dict[str, Any]]:
    """Fetch and return all scholarship records."""
    scholarships = load_scholarships()
    return [scholarship.to_dict() for scholarship in scholarships]


@app.get("/match/{roll_no}")
def match_student_scholarships(roll_no: str) -> Dict[str, Any]:
    """
    Find a student by roll_no and return all scholarships matching their profile.
    """
    students = load_students()
    target_student = next(
        (s for s in students if s.roll_no.lower() == roll_no.lower()), None
    )

    if not target_student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with roll number '{roll_no}' not found."
        )

    scholarships = load_scholarships()
    eligible_scholarships = [
        sch.to_dict() for sch in scholarships if sch.matches(target_student)
    ]

    return {
        "student": target_student.to_dict(),
        "total_matched": len(eligible_scholarships),
        "matched_scholarships": eligible_scholarships
    }


@app.get("/summary/{scholarship_id}")
def get_scholarship_summary(scholarship_id: str) -> Dict[str, Any]:
    """
    Generate an AI summary for a scholarship by ID using Ollama.
    """
    summary = generate_summary(scholarship_id)
    return {
        "scholarship_id": scholarship_id,
        "summary": summary
    }


@app.get("/policy-question/{scholarship_id}")
def ask_policy_question(scholarship_id: str, question: str) -> Dict[str, Any]:
    """
    Answer a question regarding a specific scholarship's policy using RAG grounded context.
    """
    scholarships = load_scholarships()
    target_scholarship = next(
        (s for s in scholarships if s.id.lower() == scholarship_id.lower()), None
    )

    if not target_scholarship:
        raise HTTPException(
            status_code=404,
            detail=f"Scholarship with ID '{scholarship_id}' not found."
        )

    answer = answer_policy_question(scholarship_id=target_scholarship.id, question=question)

    return {
        "scholarship_id": target_scholarship.id,
        "question": question,
        "answer": answer
    }


@app.get("/workflow/{roll_no}")
def get_workflow_state(roll_no: str) -> Dict[str, Any]:
    """
    Execute the stateful LangGraph scholarship matching workflow for a given student.
    """
    return run_scholarship_workflow(roll_no)


@app.get("/crew-workflow/{roll_no}")
def get_crew_workflow_state(roll_no: str) -> Dict[str, Any]:
    """
    Execute the CrewAI-powered stateful LangGraph scholarship workflow for a given student.
    """
    return run_scholarship_workflow(roll_no)


