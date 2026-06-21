from fastapi import FastAPI
from app.api.routes import router
from app.db.database import init_db

app = FastAPI(
    title="EU AI Act Compliance Agent",
    description="Scans AI systems for EU AI Act compliance and generates audit documentation.",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"message": "EU AI Act Compliance Agent is running"}