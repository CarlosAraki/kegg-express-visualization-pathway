"""Vercel serverless: GET /api/health"""

from fastapi import FastAPI

from server.handlers import health

app = FastAPI()


@app.get("/")
def health_route() -> dict[str, str]:
    return health()
