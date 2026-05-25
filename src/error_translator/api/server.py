"""
FastAPI Server for Error Translation.

This module exposes the error translation functionality as a RESTful web API.
It includes endpoints for single and batch translations, and serves a static
web interface. Useful for integrating the translator into web apps or distributed systems.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..core import translate_error
from importlib.metadata import version, PackageNotFoundError
import asyncio
from typing import List

# Try to determine the package version to expose in the API metadata.
try:
    VERSION = version("error-translator-cli-v2")
except PackageNotFoundError:
    VERSION = "unknown (not installed via pip)"

# Initialize the FastAPI application with basic metadata
app = FastAPI(
    title="Error translator API",
    description="An API that translates Python errors into human-readable English.",
    version=VERSION
)

# --- Pydantic Models for Request Validation ---

class ErrorRequest(BaseModel):
    """Schema for a single error translation request."""
    traceback_setting: str

class BatchErrorRequest(BaseModel):
    """Schema for translating multiple errors in a single request."""
    tracebacks: List[str]

# --- API Endpoints ---

@app.post("/translate")
def translation_endpoint(request: ErrorRequest):
    """
    Translates a single Python traceback.
    Accepts a JSON payload with a `traceback_setting` field and returns the translation.
    """
    translation_result = translate_error(request.traceback_setting)
    return translation_result


@app.post("/translate/batch")
async def batch_translation_endoint(request: BatchErrorRequest):
    """
    Translates an array of tracebacks concurrently using asyncio. 
    Ideal for processing bulk logs from message queues or distributed systems.
    """
    # Create an async task for each traceback to run them in parallel
    tasks = [
        asyncio.to_thread(translate_error, tb) for tb in request.tracebacks
    ]

    # Gather results from all tasks
    results = await asyncio.gather(*tasks)
    return {"translate_errors": results}


@app.get("/")
def read_root():
    """
    Serves the web UI index.html file at the root URL.
    Provides a simple browser-based interface for the translator.
    """
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Error translation API is running. Web UI not found. Please ensure static/index.html exists."
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint useful for monitoring systems (e.g., Kubernetes, Docker).
    """
    return {"status": "ok"}


# Mount static files directory (CSS, JS, images, etc.) so they can be loaded by the web UI
static_path = Path(__file__).with_name("static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")