from fastapi import APIRouter
from backend.services.exam_analyzer import ExamAnalyzer

router = APIRouter()

exam_service = ExamAnalyzer()


@router.post("/analyze")
def analyze_exam(topic: str, score: float, weak_areas: list[str]):
    return exam_service.analyze(topic, score, weak_areas)
