from backend.mcp_tools.applications_server import get_application_status, list_pending_applications

def test_mcp_tools():
    print("1. Testing get_application_status('EE2023313')...")
    res1 = get_application_status("EE2023313")
    print(res1)
    assert "EE2023313" in res1
    assert "SCH041" in res1
    assert "UNDER_REVIEW" in res1

    print("\n2. Testing get_application_status('INVALID_ROLL')...")
    res2 = get_application_status("INVALID_ROLL")
    print(res2)
    assert "No application records found" in res2

    print("\n3. Testing list_pending_applications()...")
    res3 = list_pending_applications()
    print(res3)
    assert "Pending / Under Review Applications" in res3
    assert "EE2023313" in res3 or "EC2022304" in res3

    print("\n[SUCCESS] All MCP Tools Unit Tests Passed!")

if __name__ == "__main__":
    test_mcp_tools()
