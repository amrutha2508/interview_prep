import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# -- Imports for Task 1 --
from task1 import app as app_task1

# -- Imports for Task 2 --
from task2 import app as app_task2

# -- Imports for Task 3 --
from task3 import app as app_task3

# Create separate clients for each task to ensure isolation
client = TestClient(app_task1)       # Used for Task 1 tests
client_v2 = TestClient(app_task2)    # Used for Task 2 tests
client_v3 = TestClient(app_task3)    # Used for Task 3 tests (MCP)

#
# TASK 1 TESTS: POST /runs
#

# -- TEST CASE 1: Happy Path (Correct Input) --
def test_create_run_success():
    payload = {
        "run_name": "test_simulation",
        "episodes": 8
    }
    response = client.post("/runs", json=payload)
    print("response retrieved:", response)
    # Check 1: Status Code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    # Check 2: run_id existence
    assert "run_id" in data, "Response JSON is missing 'run_id'"
    # Check 3: UUID format (simple check)
    assert len(data["run_id"]) == 36, "run_id does not look like a valid UUID"


# -- TEST CASE 2: Validation - Empty String --
def test_validation_empty_name():
    payload = {
        "run_name": "",  # Invalid: Empty string
        "episodes": 5
    }
    response = client.post("/runs", json=payload)
    # Pydantic should auto-generate a 422
    assert response.status_code == 422, f"Expected 422 for empty name, got {response.status_code}"


# -- TEST CASE 3: Validation - Invalid Integer --
def test_validation_invalid_episodes():
    payload = {
        "run_name": "valid_name",
        "episodes": 0  # Invalid: Must be >= 1
    }
    response = client.post("/runs", json=payload)
    assert response.status_code == 422, f"Expected 422 for 0 episodes, got {response.status_code}"


# -- TEST CASE 4: Background Task & Async Verification --
def test_background_task_triggered():
    # We mock the sleep function to ensure the background task was actually triggered
    # without actually waiting for the sleep to finish.
    with patch("task1.run_simulation_task") as mock_task:
        payload = {"run_name": "async_test", "episodes": 10}
        response = client.post("/runs", json=payload)
        assert response.status_code == 201
        # Verify the background task was added/executed
        # Note: In TestClient, background tasks run immediately after the response
        assert mock_task.called, "The background simulation task was not triggered"


#
# TASK 2 TESTS: Auth, GET /runs/{id}, Logging
#

# -- TEST CASE 5: Authentication Security --
# Purpose: Ensure the API rejects requests with missing or wrong keys.
def test_get_run_auth_security():
    run_id = "550e8400-e29b-41d4-a716-446655440000"
    # Sub-test A: Wrong Key
    headers_wrong = {"x-api-key": "wrong_password"}
    resp1 = client_v2.get(f"/runs/{run_id}", headers=headers_wrong)
    assert resp1.status_code == 401, "Should return 401 for invalid key"
    # Sub-test B: Missing Key
    resp2 = client_v2.get(f"/runs/{run_id}")
    # Accepts 401 (Unauthorized) or 422 (Validation Error)
    assert resp2.status_code in [401, 422], "Should return 401/422 for missing key"


# -- TEST CASE 6: Run Not Found --
# Purpose: Ensure 404 is returned for non-existent IDs.
def test_get_run_not_found():
    headers = {"x-api-key": "secret123"}
    fake_id = "99999999-0000-0000-0000-999999999999"
    response = client_v2.get(f"/runs/{fake_id}", headers=headers)
    assert response.status_code == 404, "Expected 404 for non-existent run"


# -- TEST CASE 7: Successful Retrieval --
# Purpose: Ensure we can retrieve a known run status.
def test_get_run_success():
    headers = {"x-api-key": "secret123"}
    # This ID is expected to exist in the starter/solution code
    valid_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client_v2.get(f"/runs/{valid_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["run_id"] == valid_id


# -- TEST CASE 8: Middleware Logging --
# Purpose: Ensure the logging middleware is active.
def test_middleware_logging():
    with patch("task2.logger") as mock_logger:
        headers = {"x-api-key": "secret123"}
        valid_id = "550e8400-e29b-41d4-a716-446655440000"
        client_v2.get(f"/runs/{valid_id}", headers=headers)

        assert mock_logger.info.called, "Middleware did not log the request"
        log_message = mock_logger.info.call_args[0][0]
        assert "GET" in log_message
        assert "200" in str(log_message)


#
# TASK 3 TESTS: MCP Interface (Tools)
#

# -- TEST CASE 9: Tool Manifest (GET /tools) --
# Purpose: Check if the manifest JSON structure is correct.
def test_mcp_list_tools():
    response = client_v3.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert isinstance(data["tools"], list)
    # Find the 'sum' tool
    sum_tool = next((t for t in data["tools"] if t.get("name") == "sum"), None)
    assert sum_tool is not None, "Tool 'sum' missing from manifest"
    assert "a" in sum_tool["parameters"]
    assert "b" in sum_tool["parameters"]


# -- TEST CASE 10: Execute Tool Success (POST /call_tool) --
# Purpose: Check if the tool actually works.
def test_mcp_call_tool_success():
    payload = {"tool": "sum", "args": {"a": 10, "b": 20}}
    response = client_v3.post("/call_tool", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["result"] == 30


# -- TEST CASE 11: Tool Error Handling --
# Purpose: Check validation for unknown tools or bad args.
def test_mcp_tool_errors():
    # Sub-test A: Unknown Tool
    payload_unknown = {"tool": "magic_wand", "args": {}}
    resp1 = client_v3.post("/call_tool", json=payload_unknown)
    assert resp1.status_code == 400, "Should 400 for unknown tool"
    # Sub-test B: Bad Arguments (String instead of int)
    payload_bad_args = {"tool": "sum", "args": {"a": "ten", "b": 5}}
    resp2 = client_v3.post("/call_tool", json=payload_bad_args)
    assert resp2.status_code == 400, "Should 400 for invalid argument type"
