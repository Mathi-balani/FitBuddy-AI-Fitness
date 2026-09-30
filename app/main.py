from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .database import init_db
from .routes import router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    version="1.0.0",
    description="AI-powered 7-day fitness plan generator with Gemini and SQLite."
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.state.templates = templates

app.include_router(router)

@app.on_event("startup")
def startup_event():
    init_db()
