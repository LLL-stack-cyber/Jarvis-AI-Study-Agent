from fastapi import APIRouter
from backend.services.exam_analyzer import ExamAnalyzer
from backend.services.paper_parser import PaperParser
from backend.services.notes_generator import NotesGenerator

router = APIRouter()

parser = PaperParser()
exam_service = ExamAnalyzer()
notes_service = NotesGenerator()


@router.post("/analyze-paper")
def analyze_paper(text: str, score: float = 60):

    # Step 1: extract questions
    questions = parser.extract_questions(text)

    # Step 2: analyze exam readiness
    analysis = exam_service.analyze(
        topic="Exam Paper",
        score=score,
        weak_areas=questions[:3] if questions else []
    )

    # Step 3: generate notes
    notes = notes_service.generate_summary("Exam Paper")

    return {
        "questions_detected": questions,
        "analysis": analysis,
        "generated_notes": notes
    }
