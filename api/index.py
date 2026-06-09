"""Vercel serverless: all /api/* routes (full paths required)."""

from __future__ import annotations

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from server.handlers import health, visualize

app = FastAPI()


@app.get("/api/health")
def health_route() -> dict[str, str]:
    return health()


@app.post("/api/visualize")
async def visualize_route(
    pathway: str = Form(...),
    file: UploadFile = File(...),
) -> JSONResponse:
    return await visualize(pathway=pathway, file=file)
