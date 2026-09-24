from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Application:
    roll_no: str
    scholarship_id: str
    status: str = "PENDING"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Application":
        return cls(
            roll_no=str(data["roll_no"]),
            scholarship_id=str(data["scholarship_id"]),
            status=str(data.get("status", "PENDING")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
