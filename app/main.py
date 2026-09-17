"""
CarbonLoop Main FastAPI Application.
Problem Statement ES-02: Monitor and reduce carbon footprints at individual and organizational levels.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.database import init_db
from app.seed import seed_demo_data
from app.routers import auth, activities, footprint, scenarios, targets, ai_insights, factors

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and seed demo data
    init_db()
    seed_demo_data()
    yield

app = FastAPI(
    title="CarbonLoop API",
    description="Closed-Loop Verifiable Carbon Accounting & Decarbonization Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(activities.router)
app.include_router(footprint.router)
app.include_router(scenarios.router)
app.include_router(targets.router)
app.include_router(ai_insights.router)
app.include_router(factors.router)

# Mount Static Files
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "CarbonLoop API is active. Navigate to /docs for interactive API documentation."}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": "CarbonLoop Deterministic Core",
        "standards": ["GHG Protocol", "CEA CO2 Baseline v20.0", "SEBI BRSR Core", "DESNZ 2024"]
    }
