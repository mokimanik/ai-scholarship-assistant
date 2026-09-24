import json
from models import Student, Scholarship, Application

def main():
    with open('data/students.json', 'r', encoding='utf-8') as f:
        students = [Student.from_dict(d) for d in json.load(f)]

    with open('data/scholarships.json', 'r', encoding='utf-8') as f:
        scholarships = [Scholarship.from_dict(d) for d in json.load(f)]

    print(f"Successfully loaded {len(students)} students and {len(scholarships)} scholarships.")

    print("\n--- Match Matrix ---")
    for s in students:
        print(f"\nStudent {s.roll_no} (Category: {s.category}, CGPA: {s.cgpa}, Income: {s.family_income}, Year: {s.year}):")
        for sch in scholarships:
            is_matched = sch.matches(s)
            status_str = "ELIGIBLE" if is_matched else "NOT ELIGIBLE"
            print(f"  - [{sch.id}] {sch.name}: {status_str}")

    sample_app = Application(roll_no=students[0].roll_no, scholarship_id=scholarships[0].id)
    print(f"\nCreated Sample Application: {sample_app}")

if __name__ == "__main__":
    main()
