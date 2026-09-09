"""FastAPI Main Entry Point for Smart Legal Metrology Package Compliance System (SIH26034)."""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .api.inspection import router as inspection_router
from .api.auth import router as auth_router

os.makedirs("data", exist_ok=True)

app = FastAPI(
    title="Smart Legal Metrology Package Compliance API",
    description="Automated label declaration extraction & deterministic compliance evaluation (SIH26034).",
    version="1.0.0",
)

# CORS Configuration
allowed_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.mount("/data", StaticFiles(directory="data"), name="data")

app.include_router(inspection_router)
app.include_router(auth_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint for system monitoring."""
    return {
        "status": "healthy",
        "service": "Legal Metrology Package Compliance Engine",
        "version": "1.0.0",
        "hackathon_problem": "SIH26034",
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Legal Metrology Package Compliance System (SIH26034)",
        "docs": "/docs",
        "health": "/api/health",
    }
