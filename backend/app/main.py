from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.get("/api/hello")
def hello():
    return {"message": "Hello, detective. Welcome to the case."}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
