from datetime import datetime, date
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

from backend.graph.state import AppState
from models.student import Student
from models.scholarship import Scholarship


def load_student_node(state: AppState) -> Dict[str, Any]:
    """Node 1: Look up student by roll_no."""
    from backend.main import load_students
    roll_no = state.get("roll_no", "")
    students = load_students()
    target_student = next(
        (s for s in students if s.roll_no.lower() == roll_no.lower()), None
    )

    if not target_student:
        return {
            "student": None,
            "needs_human_review": True
        }

    return {
        "student": target_student.to_dict(),
        "needs_human_review": False
    }


def human_review_node(state: AppState) -> Dict[str, Any]:
    """Fallback node for profiles requiring manual human review."""
    roll_no = state.get("roll_no", "")
    return {
        "final_response": f"Student profile for roll number '{roll_no}' was not found. Needs manual human review."
    }


def run_crew_node(state: AppState) -> Dict[str, Any]:
    """
    CrewAI Node: Runs Eligibility, Application Tracker, and Deadline Alert agents.
    Replaces separate match_eligibility and check_deadlines steps.
    """
    from backend.agents.crew import run_scholarship_crew
    roll_no = state.get("roll_no", "")
    crew_results = run_scholarship_crew(roll_no)

    return {
        "matched_scholarships": crew_results.get("matched_scholarships", []),
        "applications": crew_results.get("applications", []),
        "urgent_deadlines": crew_results.get("urgent_deadlines", []),
        "crew_summary": crew_results.get("crew_summary", ""),
    }


def build_response_node(state: AppState) -> Dict[str, Any]:
    """Node: Synthesizes a plain-English summary response including matched scholarships, applications, and urgent deadlines."""
    matched = state.get("matched_scholarships", [])
    urgent = state.get("urgent_deadlines", [])
    apps = state.get("applications", [])
    roll_no = state.get("roll_no", "")

    if not matched:
        summary = f"Student {roll_no} was evaluated. No matching eligible scholarships were found."
    else:
        sch_names = [f"{s['name']} (ID: {s['id']}, Amount: INR {s['amount']:,.0f})" for s in matched]
        summary = (
            f"Student {roll_no} matched {len(matched)} scholarship(s): "
            + "; ".join(sch_names)
            + "."
        )

    if apps:
        app_summary = ", ".join([f"ID {a.get('scholarship_id')}: {a.get('status')}" for a in apps])
        summary += f" Existing Application(s): [{app_summary}]."

    if urgent:
        urgent_names = [s["name"] for s in urgent]
        summary += f" WARNING: The following scholarship(s) have urgent deadlines within 5 days: {', '.join(urgent_names)}."

    return {"final_response": summary}


def route_after_student_load(state: AppState) -> str:
    """Conditional router based on needs_human_review flag."""
    if state.get("needs_human_review"):
        return "human_review_node"
    return "run_crew"


# Construct LangGraph StateGraph
builder = StateGraph(AppState)

builder.add_node("load_student", load_student_node)
builder.add_node("human_review_node", human_review_node)
builder.add_node("run_crew", run_crew_node)
builder.add_node("build_response", build_response_node)

builder.add_edge(START, "load_student")
builder.add_conditional_edges(
    "load_student",
    route_after_student_load,
    {
        "human_review_node": "human_review_node",
        "run_crew": "run_crew",
    }
)
builder.add_edge("human_review_node", END)
builder.add_edge("run_crew", "build_response")
builder.add_edge("build_response", END)

workflow_graph = builder.compile()


def run_scholarship_workflow(roll_no: str) -> Dict[str, Any]:
    """Executes the CrewAI-powered stateful scholarship workflow for a given student roll_no."""
    initial_state: AppState = {
        "roll_no": roll_no,
        "student": None,
        "matched_scholarships": [],
        "urgent_deadlines": [],
        "applications": [],
        "crew_summary": "",
        "needs_human_review": False,
        "final_response": "",
    }
    return workflow_graph.invoke(initial_state)
