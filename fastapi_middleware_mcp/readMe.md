# FastAPI + MCP Protocol (Python)

## Instructions

- Use the shortcut `Ctrl + \`` to open a terminal.
- Install required packages:
  ```
  pip install -r requirements.txt
  ```
- If you are familiar with Python notebooks, you can create `.ipynb` files for easier execution of the code, but make sure to remove them before submitting.
- Do not modify any files with the `# IMPORTANT! DO NOT MODIFY THIS FILE` comment.

---

## Running / Testing the Code

You can run/test your code using either of the following two approaches:

**Option 1:** Run the unit tests in `tests/test_main.py` using the command:
```
pytest tests/test_main.py
```

**Option 2:** Execute each task file individually.

We strongly encourage you to test your code using the provided test cases in `tests/test_main.py` before submitting.

---

## Problem Statement

### Task 1: Runs API

You are building the backend for a Job Manager Service. Your first task is to implement an endpoint that initiates a simulation run. Since simulations take time to complete, they must be processed asynchronously without blocking the HTTP response.

#### Objectives

Implement the `POST /runs` endpoint in `src/task1.py` using FastAPI.

**1. Input Validation**

The endpoint must accept a JSON payload with the following schema:

```json
{
  "run_name": "string",   // Must be non-empty
  "episodes": "integer"   // Must be >= 1
}
```

- Use Pydantic to enforce these constraints.
- Invalid inputs should automatically return `422 Unprocessable Entity`.

**2. Logic & Processing**

- **Generate an ID:** Create a unique version 4 UUID for the run.
- **Background Execution:** The simulation must run in the background.
  - You do not need to implement real simulation logic.
  - Use the provided `run_simulation_task` (or create a mock function) that sleeps for a short duration using `asyncio.sleep`.
  - Ensure the API responds immediately, before the sleep finishes.

**3. Response**

- Status code: `201 Created`
- Body:
  ```json
  {"run_id": "your-uuid-here", "status": "submitted"}
  ```

#### Setup & Constraints

- Edit `src/task1.py`.
- Do not change the function signature of the background task provided in the starter code.
- Standard FastAPI dependency injection should be used for `BackgroundTasks`.

---

### Task 2: Security & Middleware

The Job Manager Service requires better observability and security. You need to protect the status endpoint so only authorized systems can check run progress, and you must log all traffic for auditing.

#### Objectives

Edit `src/task2.py` to implement the following features.

**1. Request Logging Middleware**

Implement a global middleware that intercepts every request and logs details to the console (or logger) in this format:

```
Method: <METHOD> Path: <PATH> Status: <STATUS_CODE>
```

- **Method:** HTTP verb (GET, POST, etc.)
- **Path:** The URL path (e.g., `/runs/123`)
- **Status:** The resulting HTTP integer code (e.g., 200, 404)

**2. Implement `GET /runs/{run_id}`**

Create an endpoint to retrieve the status of a simulation run.

*Authentication:*
- The endpoint must check for a header named `x-api-key`.
- Valid Key: `"secret123"`
- If the key is missing or incorrect, return `401 Unauthorized`.

*Logic:*
- Check if `run_id` exists in the provided `RUN_DB` dictionary.
- If found: Return `200 OK` with JSON: `{"run_id": "...", "status": "..."}`
- If not found: Return `404 Not Found`.

#### Setup & Constraints

- Use the existing `RUN_DB` dictionary provided in the starter code as your data source.
- Do not modify the `RUN_DB` content, just read from it.

---

### Task 3: Minimal MCP Interface

#### Scenario

To allow AI agents to interact with your service, you need to implement a simplified version of the Model Context Protocol (MCP). This involves exposing a manifest of available functions (tools) and an endpoint to execute them.

#### Objectives

Edit `src/task3.py` to implement the following endpoints.

**1. `GET /tools`**

Return a JSON manifest describing the available tools. For this task, you only need to support one tool: `sum`.

Expected Response:
```json
{
  "tools": [
    {
      "name": "sum",
      "description": "Add two numbers",
      "parameters": ["a", "b"]
    }
  ]
}
```

**2. `POST /call_tool`**

Execute a tool based on the provided JSON payload.

Input Format:
```json
{
  "tool": "sum",
  "args": {
    "a": 3,
    "b": 5
  }
}
```

Requirements:
- **Logic:** If tool is `"sum"`, calculate `a + b` and return `{"result": 8}`.
- **Validation:**
  - Ensure `a` and `b` are valid numbers.
  - If the tool name is unknown (e.g., `"multiply"`), return `400 Bad Request`.
  - If arguments are missing or invalid, return `400 Bad Request`.
