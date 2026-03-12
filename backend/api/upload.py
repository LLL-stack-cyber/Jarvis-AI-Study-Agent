from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from backend.services.runtime import rag_engine

router = APIRouter()


class UploadResponse(BaseModel):
    filename: str
    user_id: str
    chunks_indexed: int


@router.post("/notes", response_model=UploadResponse)
async def upload_notes(
    file: UploadFile = File(...),
    user_id: str = Form(default="demo-user"),
) -> UploadResponse:
    content = (await file.read()).decode("utf-8", errors="ignore")
    chunk_count = rag_engine.ingest_notes(user_id=user_id, raw_text=content)
    return UploadResponse(
        filename=file.filename or "uploaded.txt",
        user_id=user_id,
        chunks_indexed=chunk_count,
    )
