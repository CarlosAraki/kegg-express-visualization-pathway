"""Vercel serverless: POST /api/visualize"""

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from server.handlers import visualize

app = FastAPI()


@app.post("/")
async def visualize_route(
    pathway: str = Form(...),
    file: UploadFile = File(...),
) -> JSONResponse:
    return await visualize(pathway=pathway, file=file)
