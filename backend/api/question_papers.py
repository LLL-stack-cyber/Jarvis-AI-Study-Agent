from fastapi import APIRouter
from backend.services.exam_analyzer import ExamAnalyzer
from backend.services.paper_parser import PaperParser
from backend.services.notes_generator import NotesGenerator
from backend.services.topic_classifier import TopicClassifier
from backend.services.blueprint_ai import generate_question_paper

router = APIRouter()
classifier = TopicClassifier()
parser = PaperParser()
exam_service = ExamAnalyzer()
notes_service = NotesGenerator()

@router.post("/generate-paper")
async def generate_paper(subject: str, grade: int, language: str):

    paper = generate_question_paper(subject, grade, language)

    return {
        "status": "success",
        "paper": paper
    }

@router.post("/analyze-paper")
def analyze_paper(text: str, score: float = 60):

    # Step 1: extract questions
    questions = parser.parse_questions(text)
    classified_questions = classifier.classify_questions(questions)

    # Step 2: analyze exam readiness
    analysis = exam_service.analyze(
        topic="Exam Paper",
        score=score,
        weak_areas = [q["question"] for q in questions[:3]] if questions else []
    )

    # Step 3: generate notes
    notes = notes_service.generate_summary(
        topic ="Exam Preparation",
        content = text)

    return {
        "questions":classified_questions,
        "analysis": analysis,
        "generated_notes": notes
    }
