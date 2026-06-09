"""FastAPI application."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.pipeline import PipelineError, run_pipeline

app = FastAPI(title="KEGG Expression Visualization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api.post("/visualize")
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


app.include_router(api)
