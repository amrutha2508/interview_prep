import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from langgraph.types import Command

from typing_extensions import TypedDict

from agent.index import agent_graph

app = FastAPI(title="Single Endpoint Human-in-the-Loop Agent")

# --- FastAPI Schemas ---
class AgentRequest(BaseModel):
    request: Optional[str] = Field(None, example="Write an SOP for server breaches.")
    thread_id: Optional[str] = Field(None, description="Provide this to resume an existing workflow session.")
    feedback: Optional[str] = Field("", description="Feedback to modify the section. Leave empty to approve.")

class AgentResponse(BaseModel):
    status: str
    thread_id: str
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    execution_plan: Optional[List[str]] = None
    review_payload: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    logs: List[str]

# --- API ROUTE ---
@app.post("/agent", response_model=AgentResponse)
async def handle_agent_workflow(payload: AgentRequest):
    try:
        if not payload.thread_id: 
            if not payload.request:
                raise HTTPException(status_code=400, detail="Missing 'request' parameter required to initialize a session.")
                
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            
            initial_state: AgentState = {
                "request": payload.request,
                "document_type": "",
                "plan": [],
                "current_step_index": 0,
                "document_sections": {},
                "latest_draft": "",
                "feedback": "",
                "file_path": "",
                "logs": ["Agent workflow thread spawned."]
            }
            agent_graph.invoke(initial_state, config=config)
            
        else:
            thread_id = payload.thread_id
            config = {"configurable": {"thread_id": thread_id}}
            
            if not agent_graph.get_state(config).next:
                raise HTTPException(status_code=404, detail="Active execution thread not found or session already finished.")
                
            agent_graph.invoke(Command(resume={"feedback": payload.feedback}), config=config)

        graph_state = agent_graph.get_state(config)
        
        if not graph_state.next:
            filename = os.path.basename(graph_state.values.get("file_path", ""))
            return AgentResponse(
                status="completed",
                thread_id=thread_id,
                download_url=f"/download/{filename}",
                logs=graph_state.values.get("logs", [])
            )

        review_payload = None
        if graph_state.tasks and graph_state.tasks[0].interrupts:
            review_payload = graph_state.tasks[0].interrupts[0].value

        return AgentResponse(
            status="paused_for_review",
            thread_id=thread_id,
            current_step=graph_state.values.get("current_step_index", 0) + 1,
            total_steps=len(graph_state.values.get("plan", [])),
            execution_plan=graph_state.values.get("plan", []),
            review_payload=review_payload,
            logs=graph_state.values.get("logs", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow internal breakdown: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)