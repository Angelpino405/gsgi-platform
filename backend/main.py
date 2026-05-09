from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from database import engine, Base
from routers import employees, sites, schedules, auth_router, dashboard
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GSGI Workforce Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(employees.router)
app.include_router(sites.router)
app.include_router(schedules.router)
app.include_router(dashboard.router)

FRONTEND = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(str(FRONTEND / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "GSGI Workforce Platform"}
