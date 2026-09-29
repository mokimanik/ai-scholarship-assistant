import json
from datetime import datetime, date
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

from backend import config
from models.student import Student
from models.scholarship import Scholarship
from models.application import Application

# Configure LLM explicitly for Gemini
gemini_llm = LLM(
    model=config.CREW_LLM_MODEL,
    api_key=config.GEMINI_API_KEY,
    max_retries=1
)


from backend.data_loader import load_applications, load_students, load_scholarships


@tool("Match Scholarships Tool")
def match_scholarships_tool(roll_no: str) -> str:
    """Finds eligible scholarships for a given student roll number using eligibility criteria matching."""
    from backend.main import load_students, load_scholarships
    students = load_students()
    target_student = next(
        (s for s in students if s.roll_no.lower() == roll_no.lower()), None
    )
    if not target_student:
        return f"Student with roll number '{roll_no}' not found."

    scholarships = load_scholarships()
    eligible = [sch for sch in scholarships if sch.matches(target_student)]

    if not eligible:
        return f"Student {roll_no} does not qualify for any active scholarships."

    results = []
    for sch in eligible:
        results.append(
            f"Scholarship {sch.id}: {sch.name} (Amount: INR {sch.amount:,.0f}, Min CGPA: {sch.min_cgpa}, Category: {sch.category}, Deadline: {sch.deadline})"
        )
    return f"Student {roll_no} qualifies for {len(eligible)} scholarship(s):\n" + "\n".join(results)


@tool("Track Applications Tool")
def track_applications_tool(roll_no: str) -> str:
    """Checks existing application records and their status for a student roll number."""
    apps = load_applications()
    student_apps = [a for a in apps if str(a.get("roll_no", "")).lower() == roll_no.lower()]

    if not student_apps:
        return f"No existing applications found for student roll number {roll_no}."

    app_details = [
        f"Scholarship ID {a.get('scholarship_id')}: Status = {a.get('status')}"
        for a in student_apps
    ]
    return f"Existing applications for {roll_no}:\n" + "\n".join(app_details)


@tool("Check Deadlines Tool")
def check_deadlines_tool(roll_no: str) -> str:
    """Checks matched scholarship deadlines for a student roll number. ONLY flags deadlines with days_remaining <= 5 as URGENT, otherwise marks them as ON SCHEDULE."""
    from backend.main import load_students, load_scholarships
    students = load_students()
    target_student = next(
        (s for s in students if s.roll_no.lower() == roll_no.lower()), None
    )
    if not target_student:
        return f"Student with roll number '{roll_no}' not found."

    scholarships = load_scholarships()
    eligible = [sch for sch in scholarships if sch.matches(target_student)]
    today = date.today()

    urgent = []
    on_schedule = []
    for sch in eligible:
        try:
            deadline_date = datetime.strptime(sch.deadline, "%Y-%m-%d").date()
            days_left = (deadline_date - today).days
            if 0 <= days_left <= 5:
                urgent.append(f"{sch.name} (ID: {sch.id}) - Deadline: {sch.deadline} ({days_left} days remaining) [URGENT]")
            elif days_left > 5:
                on_schedule.append(f"{sch.name} (ID: {sch.id}) - Deadline: {sch.deadline} ({days_left} days remaining) [ON SCHEDULE]")
        except ValueError:
            pass

    report_lines = []
    if urgent:
        report_lines.append("URGENT DEADLINES (days_remaining <= 5):\n" + "\n".join(urgent))
    if on_schedule:
        report_lines.append("ON SCHEDULE DEADLINES (days_remaining > 5):\n" + "\n".join(on_schedule))

    if not report_lines:
        return "No active scholarship deadlines found."

    return "\n\n".join(report_lines)


# Define CrewAI Agents with iteration limits, execution timeouts, using Gemini LLM
eligibility_agent = Agent(
    role="Scholarship Eligibility Specialist",
    goal="Match a student's profile against scholarship criteria and explain why they qualify or don't.",
    backstory="You are an expert academic advisor who matches students to financial aid and scholarship programs.",
    tools=[match_scholarships_tool],
    llm=gemini_llm,
    max_iter=3,
    max_execution_time=15,
    verbose=False
)

application_tracker_agent = Agent(
    role="Application Tracker Specialist",
    goal="Check existing application history and statuses for students.",
    backstory="You are a meticulous record keeper responsible for tracking student scholarship applications.",
    tools=[track_applications_tool],
    llm=gemini_llm,
    max_iter=3,
    max_execution_time=15,
    verbose=False
)

deadline_alert_agent = Agent(
    role="Deadline & Urgency Alert Specialist",
    goal="Review matched scholarship deadlines. Flag ONLY deadlines with days_remaining <= 5 as urgent. If days_remaining > 5, explicitly report the deadline as 'on schedule'.",
    backstory="You are a precise deadline coordinator. You strictly call a deadline 'urgent' ONLY if days_remaining <= 5. For any deadline with days_remaining > 5, you explicitly state that it is 'on schedule'.",
    tools=[check_deadlines_tool],
    llm=gemini_llm,
    max_iter=3,
    max_execution_time=15,
    verbose=False
)


def run_scholarship_crew(roll_no: str) -> Dict[str, Any]:
    """
    Executes the 3-agent CrewAI pipeline sequentially and returns combined structured results.
    """
    from backend.main import load_students, load_scholarships

    # Deterministic Data Retrieval for structured response
    students = load_students()
    target_student = next(
        (s for s in students if s.roll_no.lower() == roll_no.lower()), None
    )

    if not target_student:
        return {
            "matched_scholarships": [],
            "applications": [],
            "urgent_deadlines": [],
            "crew_summary": f"Student profile for roll number '{roll_no}' not found."
        }

    scholarships = load_scholarships()
    matched_objs = [sch for sch in scholarships if sch.matches(target_student)]
    matched_dicts = [sch.to_dict() for sch in matched_objs]

    all_apps = load_applications()
    student_apps = [a for a in all_apps if str(a.get("roll_no", "")).lower() == roll_no.lower()]

    today = date.today()
    urgent_dicts = []
    for sch in matched_objs:
        try:
            deadline_date = datetime.strptime(sch.deadline, "%Y-%m-%d").date()
            days_left = (deadline_date - today).days
            if 0 <= days_left <= 5:
                urgent_dicts.append(sch.to_dict())
        except ValueError:
            pass

    # Tasks definition
    t1 = Task(
        description=f"Evaluate eligibility for student roll number '{roll_no}' using the match_scholarships_tool.",
        expected_output="Detailed eligibility matching report.",
        agent=eligibility_agent
    )

    t2 = Task(
        description=f"Track existing application status for student roll number '{roll_no}' using the track_applications_tool.",
        expected_output="Existing application status report.",
        agent=application_tracker_agent
    )

    t3 = Task(
        description=(
            f"Identify scholarship deadlines for student roll number '{roll_no}' using the check_deadlines_tool. "
            f"STRICT RULE: Only flag a deadline as 'urgent' if days_remaining <= 5. "
            f"If days_remaining > 5, explicitly state that the deadline is 'on schedule'."
        ),
        expected_output="Deadline urgency report marking deadlines with days_remaining <= 5 as urgent, and all others as on schedule.",
        agent=deadline_alert_agent
    )

    crew = Crew(
        agents=[eligibility_agent, application_tracker_agent, deadline_alert_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=False
    )

    try:
        crew_output = crew.kickoff(inputs={"roll_no": roll_no})
        summary_text = str(crew_output)
    except Exception as e:
        # Fallback summary formatting if LLM inference is unconfigured locally
        summary_text = (
            f"Eligibility: Matched {len(matched_dicts)} scholarship(s). "
            f"Applications: Found {len(student_apps)} existing record(s). "
            f"Deadlines: {len(urgent_dicts)} urgent deadline(s) flagged."
        )

    return {
        "matched_scholarships": matched_dicts,
        "applications": student_apps,
        "urgent_deadlines": urgent_dicts,
        "crew_summary": summary_text
    }
