"""FastAPI application for local development."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.handlers import health, visualize

app = FastAPI(title="KEGG Expression Visualization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.get("/api/health")(health)
app.post("/api/visualize")(visualize)
