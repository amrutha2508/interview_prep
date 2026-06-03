import logging
from fastapi import FastAPI, Request, HTTPException, Header, status
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_logger")

app = FastAPI()

RUN_DB = {
    "550e8400-e29b-41d4-a716-446655440000": "completed",
    "123e4567-e89b-12d3-a456-426614174000": "running"
}

# TODO: 1. Implement Middleware
# Requirement: Log every request in the format: "Method: <METHOD> Path: <PATH> Status: <STATUS_CODE>"
# Tip: Use @app.middleware("http")
@app.middleware("http")
async def log_requests(request:Request, call_next):
    response = await call_next(request)
    logger.info(f"Method: {request.method} Path: {request.url.path} Status: {response.status_code}")
    return response


# TODO: 2. Implement GET /runs/{run_id}
# Requirements:
# - Accept 'run_id' as a path parameter.
# - Accept 'x-api-key' in the header.
# - Validate Header: If key != "secret123" return 401 Unauthorized.
# - Check DB: If run_id not in RUN_DB, return 404 Not Found.
# - Success: Return JSON {"run_id": ..., "status": ...}

@app.get("/runs/{run_id}")
async def get_run_status(run_id:str, x_api_key:str = Header(...)):
    if x_api_key != "secret123":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if run_id not in RUN_DB.keys():
        raise HTTPException(status_code=404, detail="Run not found")

    return {"run_id": run_id, "status": RUN_DB[run_id]}