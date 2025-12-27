import os
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
import datetime
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_SERVICE_URI = "sqlite:///./sessions.db"
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
SERVE_WEB_INTERFACE = True



# 2. The session service also needs to be a URI.
# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    trace_to_cloud=False,

)


SERVICE_VERSION = "1.0.0"
LAST_DEPLOYED = os.environ.get("LAST_DEPLOYED", datetime.datetime.utcnow().isoformat())
LAST_UPDATED = os.environ.get("LAST_UPDATED", datetime.datetime.utcnow().isoformat())
SERVICE_NAME = "Search Agent"

@app.get("/metadata")
async def metadata():
    return {
        "service_name": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "last_deployed": LAST_DEPLOYED,
        "last_updated": LAST_UPDATED,
        "host": os.environ.get("HOSTNAME", "unknown"),
    }
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

@app.get("/metadata")
async def metadata():
    ...


# You can add more FastAPI routes or configurations below if needed
# Example:
# @app.get("/hello")
# async def read_root():
#     return {"Hello": "World"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))