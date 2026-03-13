import logging
from pathlib import Path
from typing import Dict, List, Tuple

from backend.api import notes, quiz
from backend.services import document_loader, topic_classifier

logger = logging.getLogger(__name__)


def _classify_topic(query: str) -> str:
    """Classify a query topic using available classifier interfaces."""
    try:
        if hasattr(topic_classifier, "classify_topic"):
            return str(topic_classifier.classify_topic(query))

        if hasattr(topic_classifier, "TopicClassifier"):
            return str(topic_classifier.TopicClassifier().classify_question(query))

        logger.warning("No supported topic classification interface found")
    except Exception as exc:
        logger.exception("Failed to classify topic: %s", exc)

    return "general"


def _candidate_document_paths(user_id: str, topic: str) -> List[Path]:
    """Return candidate document paths to attempt loading from."""
    base = Path("data") / user_id
    return [
        base / f"{topic}.txt",
        base / f"{topic}.md",
        base / "notes.txt",
    ]


def _retrieve_documents(user_id: str, topic: str) -> Tuple[List[str], List[str]]:
    """Load relevant documents and return (document_names, document_contents)."""
    source_docs: List[str] = []
    contents: List[str] = []

    if not hasattr(document_loader, "load_document"):
        logger.warning("document_loader.load_document is not available")
        return source_docs, contents

    for path in _candidate_document_paths(user_id=user_id, topic=topic):
        if not path.exists():
            continue

        try:
            document_text = document_loader.load_document(str(path))
            if not document_text:
                continue
            source_docs.append(path.name)
            contents.append(str(document_text))
        except Exception as exc:
            logger.exception("Failed to load document %s: %s", path, exc)

    return source_docs, contents


def _build_response_text(query: str, topic: str, documents: List[str]) -> str:
    """Generate a concise tutor response from query and supporting documents."""
    context_snippet = documents[0][:300] if documents else "No source notes were found."
    return (
        f"Topic: {topic}\n"
        f"Question: {query}\n"
        f"Tutor response: Start with core definitions, then apply one solved example.\n"
        f"Context: {context_snippet}"
    )


def process_student_query(user_id: str, query: str) -> dict:
    """Process a student query and return topic, response, and source document names."""
    try:
        if not query or not query.strip():
            return {"topic": "general", "response_text": "Please provide a valid query.", "source_docs": []}

        topic = _classify_topic(query)
        source_docs, contents = _retrieve_documents(user_id=user_id, topic=topic)
        answer = _build_response_text(query=query, topic=topic, documents=contents)

        return {"topic": topic, "response_text": answer, "source_docs": source_docs}
    except Exception as exc:
        logger.exception("process_student_query failed for user=%s: %s", user_id, exc)
        return {"topic": "general", "response_text": "Unable to process your query right now.", "source_docs": []}


def _build_quiz_questions(query: str) -> List[str]:
    """Create a small quiz from a user query."""
    return [
        f"1. Define the main concept in: {query}",
        f"2. Give one real-world application related to: {query}",
        f"3. Solve one short problem based on: {query}",
    ]


def generate_quiz_from_query(user_id: str, query: str) -> dict:
    """Create and store a 3-question quiz using quiz.create_quiz."""
    try:
        questions = _build_quiz_questions(query)

        if hasattr(quiz, "create_quiz"):
            quiz_id = quiz.create_quiz(user_id, questions)
        else:
            logger.warning("quiz.create_quiz is not available; using local fallback quiz_id")
            quiz_id = f"quiz-{user_id}-{abs(hash(query)) % 100000}"

        return {"quiz_id": quiz_id, "questions": questions}
    except Exception as exc:
        logger.exception("generate_quiz_from_query failed for user=%s: %s", user_id, exc)
        return {"quiz_id": None, "questions": []}


def save_student_notes(user_id: str, title: str, content: str) -> dict:
    """Save student notes using notes.save_note and return status."""
    try:
        if hasattr(notes, "save_note"):
            result = notes.save_note(user_id, title, content)
            return {"success": bool(result), "note": result}

        logger.warning("notes.save_note is not available")
        return {"success": False, "error": "save_note interface unavailable"}
    except Exception as exc:
        logger.exception("save_student_notes failed for user=%s: %s", user_id, exc)
        return {"success": False, "error": "failed to save note"}
