from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.database import init_db

app = FastAPI(
    title="EU AI Act Compliance Agent",
    description="Scans AI systems for EU AI Act compliance and generates audit documentation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"message": "EU AI Act Compliance Agent is running"}