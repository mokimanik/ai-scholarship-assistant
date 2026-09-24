from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Student:
    roll_no: str
    category: str
    cgpa: float
    family_income: float
    year: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        return cls(
            roll_no=str(data["roll_no"]),
            category=str(data["category"]),
            cgpa=float(data["cgpa"]),
            family_income=float(data["family_income"]),
            year=int(data["year"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
