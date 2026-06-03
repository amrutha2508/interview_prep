from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any

#
# TASK 3: Minimal MCP (Model Context Protocol)
#

# Create FastAPI app instance
app = FastAPI()

# TODO: 1. Implement GET /tools
# Requirements:
# - Return a JSON object listing available tools.
# - Currently, only support one tool: "sum"
# - "sum" takes parameters "a" and "b".

# TODO: 2. Implement POST /call_tool
# Requirements:
# - Accept JSON: {"tool": "name", "args": {...}}
# - If tool is "sum", return {"result": a + b}
# - Validate that 'a' and 'b' are numbers.
# - Handle unknown tools or bad arguments with HTTP 400.

@app.get("/tools")
async def list_tools():
    tools = [{
      "name": "sum",
      "description": "Add two numbers",
      "parameters": ["a", "b"]
    }]
    return {"tools": tools}

@app.post("/call_tool")
async def call_tool(payload: Dict[str, Any] = Body(...)):
    if payload["tool"] == "sum":
        a = payload["args"].get("a")
        b = payload["args"].get("b")
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise HTTPException(status_code=400, detail="Invalid arguments for 'sum' tool")
        return {"result": a + b}
    raise HTTPException(status_code=400, detail="Unknown tool")