import logging
from pathlib import Path
from typing import List, Dict, Any, Union
import pandas as pd

from backend import config
from models.student import Student
from models.scholarship import Scholarship

logger = logging.getLogger(__name__)


def _get_excel_path(file_path: Union[str, Path, None] = None) -> Path:
    if file_path is None:
        return config.EXCEL_FILE_PATH
    return Path(file_path)


def load_students(file_path: Union[str, Path, None] = None) -> List[Student]:
    """
    Reads the 'Students' sheet from the Excel file using pandas
    and returns a list of Student objects. Skips malformed rows gracefully.
    """
    excel_path = _get_excel_path(file_path)
    if not excel_path.exists():
        logger.warning(f"Excel file not found at: {excel_path}")
        return []

    try:
        df = pd.read_excel(excel_path, sheet_name="Students")
    except Exception as e:
        logger.warning(f"Error reading 'Students' sheet from {excel_path}: {e}")
        return []

    students: List[Student] = []
    for idx, row in df.iterrows():
        try:
            if pd.isna(row.get("roll_no")) or pd.isna(row.get("category")):
                logger.warning(f"Skipping row {idx} in Students sheet due to missing required fields.")
                continue

            student_data = {
                "roll_no": str(row["roll_no"]).strip(),
                "name": str(row.get("name", "")).strip(),
                "category": str(row["category"]).strip(),
                "cgpa": float(row["cgpa"]),
                "family_income": float(row["family_income"]),
                "year": int(row["year"]),
            }
            students.append(Student.from_dict(student_data))
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Skipping malformed student row {idx}: {e}")

    return students


def load_scholarships(file_path: Union[str, Path, None] = None) -> List[Scholarship]:
    """
    Reads the 'Scholarships' sheet from the Excel file using pandas
    and returns a list of Scholarship objects. Skips malformed rows gracefully.
    """
    excel_path = _get_excel_path(file_path)
    if not excel_path.exists():
        logger.warning(f"Excel file not found at: {excel_path}")
        return []

    try:
        df = pd.read_excel(excel_path, sheet_name="Scholarships")
    except Exception as e:
        logger.warning(f"Error reading 'Scholarships' sheet from {excel_path}: {e}")
        return []

    scholarships: List[Scholarship] = []
    for idx, row in df.iterrows():
        try:
            if pd.isna(row.get("id")) or pd.isna(row.get("name")):
                logger.warning(f"Skipping row {idx} in Scholarships sheet due to missing required fields.")
                continue

            # Parse eligible_years
            raw_years = row.get("eligible_years")
            eligible_years: List[int] = []
            if not pd.isna(raw_years):
                years_str = str(raw_years)
                for part in years_str.split(","):
                    part = part.strip()
                    if part:
                        try:
                            eligible_years.append(int(float(part)))
                        except ValueError:
                            pass

            # Parse required_docs
            raw_docs = row.get("required_docs")
            required_docs: List[str] = []
            if not pd.isna(raw_docs):
                docs_str = str(raw_docs)
                required_docs = [d.strip() for d in docs_str.split(",") if d.strip()]

            # Deadline formatting
            raw_deadline = row.get("deadline")
            deadline_str = ""
            if not pd.isna(raw_deadline):
                if isinstance(raw_deadline, pd.Timestamp):
                    deadline_str = raw_deadline.strftime("%Y-%m-%d")
                else:
                    deadline_str = str(raw_deadline).strip()

            scholarship_data = {
                "id": str(row["id"]).strip(),
                "name": str(row["name"]).strip(),
                "sponsor": str(row.get("sponsor", "")).strip(),
                "category": str(row.get("category", "ALL")).strip(),
                "min_cgpa": float(row["min_cgpa"]),
                "max_family_income": float(row["max_family_income"]),
                "eligible_years": eligible_years,
                "amount": float(row["amount"]),
                "deadline": deadline_str,
                "required_docs": required_docs,
            }
            scholarships.append(Scholarship.from_dict(scholarship_data))
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Skipping malformed scholarship row {idx}: {e}")

    return scholarships


def load_applications(file_path: Union[str, Path, None] = None) -> List[Dict[str, Any]]:
    """
    Reads the 'Applications' sheet from the Excel file using pandas
    and returns a list of Application dictionaries. Skips malformed rows gracefully.
    """
    excel_path = _get_excel_path(file_path)
    if not excel_path.exists():
        logger.warning(f"Excel file not found at: {excel_path}")
        return []

    try:
        df = pd.read_excel(excel_path, sheet_name="Applications")
    except Exception as e:
        logger.warning(f"Error reading 'Applications' sheet from {excel_path}: {e}")
        return []

    applications: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        try:
            if pd.isna(row.get("roll_no")) or pd.isna(row.get("scholarship_id")):
                logger.warning(f"Skipping row {idx} in Applications sheet due to missing required fields.")
                continue

            raw_date = row.get("applied_date")
            applied_date_str = ""
            if not pd.isna(raw_date):
                if isinstance(raw_date, pd.Timestamp):
                    applied_date_str = raw_date.strftime("%Y-%m-%d")
                else:
                    applied_date_str = str(raw_date).strip()

            app_data = {
                "application_id": str(row.get("application_id", "")).strip(),
                "roll_no": str(row["roll_no"]).strip(),
                "scholarship_id": str(row["scholarship_id"]).strip(),
                "status": str(row.get("status", "PENDING")).strip(),
                "applied_date": applied_date_str,
            }
            applications.append(app_data)
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Skipping malformed application row {idx}: {e}")

    return applications
