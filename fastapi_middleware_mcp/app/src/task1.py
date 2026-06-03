import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# TODO: Define the Pydantic Model 'RunRequest' here
# Requirements:
# - run_name: non-empty string
# - episodes: integer >= 1

class RunRequest(BaseModel):
    run_name: str = Field(...,min_length=1)
    episodes: int = Field(..., ge=1)


async def run_simulation_task(run_id: str, episodes: int):
    await asyncio.sleep(1)
    print(f"Run {run_id} completed.")


# TODO: Implement the POST /runs endpoint
# 1. Validate input using RunRequest
# 2. Generate a UUID v4
# 3. Add run_simulation_task to background_tasks
# 4. Return status 201 and the run_id

@app.post("/runs", status_code=201)
async def create_run(run_request: RunRequest, bg: BackgroundTasks):
    run_id = str(uuid.uuid4())
    await run_simulation_task(run_id=run_id, episodes=run_request.episodes)
    bg.add_task(run_simulation_task, run_id=run_id, episodes=run_request.episodes)
    return {"run_id": run_id,"status":"submitted"}
    
