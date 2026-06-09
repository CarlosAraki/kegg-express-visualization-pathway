"""Shared API handlers for local uvicorn and Vercel serverless."""

from __future__ import annotations

from fastapi import File, Form, UploadFile
from fastapi.responses import JSONResponse

from server.pipeline import PipelineError, run_pipeline


def health() -> dict[str, str]:
    return {"status": "ok"}


async def visualize(
    pathway: str = Form(...),
    file: UploadFile = File(...),
) -> JSONResponse:
    try:
        content = await file.read()
        payload = run_pipeline(pathway, content)
        return JSONResponse(payload)
    except PipelineError as exc:
        body = {"error": str(exc), **exc.details}
        return JSONResponse(body, status_code=400)
    except Exception:
        return JSONResponse(
            {"error": "Unexpected server error. Please try again."},
            status_code=500,
        )
