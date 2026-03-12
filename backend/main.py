from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.auth import router as auth_router
from backend.api.mentor import router as mentor_router
from backend.api.quiz import router as quiz_router
from backend.api.upload import router as upload_router

app = FastAPI(title="Jarvis AI Study Agent", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(upload_router, prefix="/api/upload", tags=["upload"])
app.include_router(quiz_router, prefix="/api/quiz", tags=["quiz"])
app.include_router(mentor_router, prefix="/api/mentor", tags=["mentor"])


@app.get("/")
def root() -> dict:
    return {"message": "Jarvis AI Study Agent API"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "jarvis-backend"}
