import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.orchestrator import run_research_async
from core.config import get_missing_env_vars, load_project_env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_project_env()

# Initialize FastAPI app
app = FastAPI(title="ResearchSwarm API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Cache-Control"],
)


# Request/Response Models
class ResearchRequest(BaseModel):
    question: str


class CritiqueResponse(BaseModel):
    flagged_claims: List[str]
    gaps: List[str]
    confidence_score: int


class ResearchResponse(BaseModel):
    report: str
    critique: CritiqueResponse


class HealthResponse(BaseModel):
    status: str


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "ok"}


# Research Endpoint with Streaming Response
@app.post("/research")
async def research(request: ResearchRequest):
    """
    Execute research on the given question with streaming response.
    
    Streams two Server-Sent Events (SSE):
    1. Report event: { "type": "report", "report": "markdown string" }
    2. Critique event: { "type": "critique", "critique": {...} }
    
    Args:
        request: ResearchRequest containing the question
    
    Returns:
        StreamingResponse with SSE events
    
    Raises:
        HTTPException: If research fails or question is empty
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    missing = get_missing_env_vars(["GROQ_API_KEY", "TAVILY_API_KEY"])
    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Research failed: missing required environment variables: "
                + ", ".join(missing)
                + ". Add them to the project .env file."
            ),
        )
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE progress, report, and critique events."""
        try:
            logger.info(f"Starting research for question: {request.question}")

            progress_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

            def publish_progress(event: Dict[str, Any]) -> None:
                progress_queue.put_nowait(event)

            task = asyncio.create_task(
                run_research_async(request.question, progress_callback=publish_progress)
            )

            while True:
                if task.done() and progress_queue.empty():
                    break

                try:
                    progress_event = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                normalized_progress_event = {
                    "type": "progress",
                    "agent": str(progress_event.get("agent", "")),
                    "status": str(progress_event.get("status", "")),
                    "detail": str(progress_event.get("detail", "")),
                }
                yield f"data: {json.dumps(normalized_progress_event)}\n\n"

            report, critique = await task
            
            logger.info("Research completed successfully")
            
            # Ensure report is a string
            report_str = str(report) if report else ""
            
            report_event = {
                "type": "report",
                "report": report_str
            }
            yield f"data: {json.dumps(report_event)}\n\n"
            
            # Prepare critique response
            if not isinstance(critique, dict):
                critique = {}
            
            critique_response = {
                "flagged_claims": critique.get("flagged_claims", []),
                "gaps": critique.get("gaps", []),
                "confidence_score": int(critique.get("confidence_score", 0))
            }
            
            # Stream the critique event
            critique_event = {
                "type": "critique",
                "critique": critique_response
            }
            yield f"data: {json.dumps(critique_event)}\n\n"
            
        except Exception as e:
            error_message = str(e)
            if "invalid_api_key" in error_message.lower() or "invalid api key" in error_message.lower():
                error_message = (
                    "Invalid GROQ_API_KEY. Update GROQ_API_KEY in .env, then restart the backend server."
                )

            logger.error(f"Research failed: {error_message}")
            error_event = {
                "type": "error",
                "error": error_message
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
