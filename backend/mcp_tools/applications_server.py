import sys
from pathlib import Path

# Add project root to sys.path when script is executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

from backend import config


# Initialize FastMCP Server
mcp = FastMCP("Applications Server")


from backend.data_loader import load_applications


@mcp.tool()
def get_application_status(roll_no: str) -> str:
    """
    Returns the application status for a given student roll number.
    
    Args:
        roll_no: Student roll number (e.g., 'CS2023001')
    """
    apps = load_applications()
    matched_apps = [
        a for a in apps if str(a.get("roll_no", "")).lower() == roll_no.lower()
    ]

    if not matched_apps:
        return f"No application records found for student roll number '{roll_no}'."

    results = []
    for app in matched_apps:
        results.append(
            f"Scholarship ID: {app.get('scholarship_id')}, Status: {app.get('status')}"
        )

    return f"Applications for {roll_no}:\n" + "\n".join(results)


@mcp.tool()
def list_pending_applications() -> str:
    """
    Returns all applications currently under review or pending.
    """
    apps = load_applications()
    pending_statuses = {"under_review", "under review", "pending"}
    
    pending_apps = [
        a for a in apps
        if str(a.get("status", "")).lower().replace("-", "_") in pending_statuses
    ]

    if not pending_apps:
        return "No pending or under-review applications found."

    results = []
    for app in pending_apps:
        results.append(
            f"Student Roll No: {app.get('roll_no')}, Scholarship ID: {app.get('scholarship_id')}, Status: {app.get('status')}"
        )

    return f"Pending / Under Review Applications ({len(pending_apps)} total):\n" + "\n".join(results)


if __name__ == "__main__":
    mcp.run()
