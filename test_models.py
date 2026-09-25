from models import Application
from backend.data_loader import load_students, load_scholarships

def main():
    students = load_students()
    scholarships = load_scholarships()

    print(f"Successfully loaded {len(students)} students and {len(scholarships)} scholarships.")

    print("\n--- Match Matrix ---")
    for s in students[:3]:
        print(f"\nStudent {s.roll_no} (Category: {s.category}, CGPA: {s.cgpa}, Income: {s.family_income}, Year: {s.year}):")
        for sch in scholarships[:5]:
            is_matched = sch.matches(s)
            status_str = "ELIGIBLE" if is_matched else "NOT ELIGIBLE"
            print(f"  - [{sch.id}] {sch.name}: {status_str}")

    sample_app = Application(roll_no=students[0].roll_no, scholarship_id=scholarships[0].id)
    print(f"\nCreated Sample Application: {sample_app}")

if __name__ == "__main__":
    main()
