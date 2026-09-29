from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api():
    print("1. Testing GET /health...")
    res_health = client.get("/health")
    print(f"Status: {res_health.status_code}, Body: {res_health.json()}")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "ok"}

    print("\n2. Testing GET /students...")
    res_students = client.get("/students")
    print(f"Status: {res_students.status_code}, Count: {len(res_students.json())}")
    assert res_students.status_code == 200
    assert len(res_students.json()) == 100

    print("\n3. Testing GET /scholarships...")
    res_scholarships = client.get("/scholarships")
    print(f"Status: {res_scholarships.status_code}, Count: {len(res_scholarships.json())}")
    assert res_scholarships.status_code == 200
    assert len(res_scholarships.json()) == 100

    print("\n4. Testing GET /match/CE2021026...")
    res_match = client.get("/match/CE2021026")
    print(f"Status: {res_match.status_code}")
    data = res_match.json()
    print(f"Student: {data['student']['roll_no']}")
    print(f"Total Matched: {data['total_matched']}")
    print("Matched Scholarships:")
    for sch in data['matched_scholarships']:
        print(f"  - [{sch['id']}] {sch['name']}")
    assert res_match.status_code == 200
    assert data["total_matched"] == 8

    print("\n5. Testing GET /match/INVALID_ROLL (404 expected)...")
    res_404 = client.get("/match/INVALID_ROLL")
    print(f"Status: {res_404.status_code}, Detail: {res_404.json()['detail']}")
    assert res_404.status_code == 404

    print("\n6. Testing GET /summary/INVALID_SCH (404 expected)...")
    res_sum_404 = client.get("/summary/INVALID_SCH")
    print(f"Status: {res_sum_404.status_code}, Detail: {res_sum_404.json()['detail']}")
    assert res_sum_404.status_code == 404

    print("\n7. Testing GET /summary/SCH001 (Mocked Gemini call)...")
    with patch("backend.ai_client.generate_scholarship_summary") as mock_gen:
        mock_gen.return_value = "This scholarship offers financial assistance to eligible students."
        res_sum = client.get("/summary/SCH001")
        print(f"Status: {res_sum.status_code}, Body: {res_sum.json()}")
        assert res_sum.status_code == 200
        assert res_sum.json()["scholarship_id"] == "SCH001"
        assert res_sum.json()["summary"] == "This scholarship offers financial assistance to eligible students."

    print("\n8. Testing GET /policy-question/INVALID_SCH (404 expected)...")
    res_pq_404 = client.get("/policy-question/INVALID_SCH?question=What+is+the+deadline")
    print(f"Status: {res_pq_404.status_code}, Detail: {res_pq_404.json()['detail']}")
    assert res_pq_404.status_code == 404

    print("\n9. Testing GET /policy-question/SCH001 (Mocked QA Chain)...")
    with patch("backend.main.answer_policy_question") as mock_qa:
        mock_qa.return_value = "Appeals must be submitted to the Grievance Redressal Cell within 15 calendar days."
        res_pq = client.get("/policy-question/SCH001?question=What+is+the+appeal+process")
        print(f"Status: {res_pq.status_code}, Body: {res_pq.json()}")
        assert res_pq.status_code == 200
        assert res_pq.json()["scholarship_id"] == "SCH001"
        assert res_pq.json()["question"] == "What is the appeal process"
        assert "Grievance Redressal Cell" in res_pq.json()["answer"]

    print("\n10. Testing GET /workflow/CE2021026 (LangGraph Workflow)...")
    res_wf = client.get("/workflow/CE2021026")
    print(f"Status: {res_wf.status_code}")
    wf_data = res_wf.json()
    print(f"Needs Human Review: {wf_data['needs_human_review']}")
    print(f"Matched Count: {len(wf_data['matched_scholarships'])}")
    print(f"Final Response: {wf_data['final_response']}")
    assert res_wf.status_code == 200
    assert wf_data["needs_human_review"] is False
    assert len(wf_data["matched_scholarships"]) == 8
    assert "CE2021026" in wf_data["final_response"]

    print("\n11. Testing GET /workflow/INVALID_ROLL (LangGraph Human Review Fallback)...")
    res_wf_invalid = client.get("/workflow/INVALID_ROLL")
    print(f"Status: {res_wf_invalid.status_code}")
    wf_invalid_data = res_wf_invalid.json()
    print(f"Needs Human Review: {wf_invalid_data['needs_human_review']}")
    print(f"Final Response: {wf_invalid_data['final_response']}")
    assert res_wf_invalid.status_code == 200
    assert wf_invalid_data["needs_human_review"] is True
    assert "manual human review" in wf_invalid_data["final_response"].lower()

    print("\n12. Testing GET /crew-workflow/CE2021026 (CrewAI + LangGraph)...")
    res_cwf = client.get("/crew-workflow/CE2021026")
    print(f"Status: {res_cwf.status_code}")
    cwf_data = res_cwf.json()
    print(f"Needs Human Review: {cwf_data['needs_human_review']}")
    print(f"Matched Count: {len(cwf_data['matched_scholarships'])}")
    print(f"Applications Found: {len(cwf_data['applications'])}")
    print(f"Crew Summary: {cwf_data['crew_summary']}")
    assert res_cwf.status_code == 200
    assert cwf_data["needs_human_review"] is False
    assert len(cwf_data["matched_scholarships"]) == 8


    print("\n[SUCCESS] All FastAPI Endpoint Tests Passed!")

if __name__ == "__main__":
    test_api()


