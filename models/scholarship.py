from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from models.student import Student


@dataclass
class Scholarship:
    id: str
    name: str
    category: str
    min_cgpa: float
    max_family_income: float
    eligible_years: List[int]
    amount: float
    deadline: str
    required_docs: List[str]

    def matches(self, student: Student) -> bool:
        """
        Check if a student meets all eligibility criteria for this scholarship.
        """
        # Category check: match specific category or wildcard 'ALL'
        category_match = (
            self.category.upper() == "ALL" or
            self.category.upper() == student.category.upper()
        )

        # CGPA check: student CGPA must meet or exceed minimum CGPA requirement
        cgpa_match = student.cgpa >= self.min_cgpa

        # Income check: student family income must not exceed maximum limit
        income_match = student.family_income <= self.max_family_income

        # Academic year check: student's year must be in the list of eligible years
        year_match = student.year in self.eligible_years

        return category_match and cgpa_match and income_match and year_match

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scholarship":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            min_cgpa=float(data["min_cgpa"]),
            max_family_income=float(data["max_family_income"]),
            eligible_years=[int(y) for y in data.get("eligible_years", [])],
            amount=float(data["amount"]),
            deadline=str(data["deadline"]),
            required_docs=[str(d) for d in data.get("required_docs", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
