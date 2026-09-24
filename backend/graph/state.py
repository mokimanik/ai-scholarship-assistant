from typing import TypedDict, Optional, List, Dict, Any


class AppState(TypedDict):
    roll_no: str
    student: Optional[Dict[str, Any]]
    matched_scholarships: List[Dict[str, Any]]
    urgent_deadlines: List[Dict[str, Any]]
    applications: List[Dict[str, Any]]
    crew_summary: Optional[str]
    needs_human_review: bool
    final_response: str
