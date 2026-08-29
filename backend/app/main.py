import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.api.inspection import router as inspection_router

app = FastAPI(
    title="Smart Legal Metrology Package Compliance API",
    description="SIH26034 Prototype V1 — Automated Label Extraction & Deterministic Rule Compliance Engine",
    version="1.0.0",
)

# CORS Configuration for local development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inspection_router)


@app.get("/")
def root():
    return {
        "title": "Smart Legal Metrology Compliance System API",
        "problem_statement": "SIH26034",
        "docs": "/docs",
        "health": "/api/inspection/health",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
