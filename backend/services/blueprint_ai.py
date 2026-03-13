import logging
from typing import Any, Dict, List

from backend.services.topic_classifier import TopicClassifier
try:
    from backend.services.translation_service import TranslationService
except Exception:  # pragma: no cover - dependency fallback
    class TranslationService:  # type: ignore[override]
        def translate_text(self, text: str, target_language: str) -> str:
            return text


try:
    from backend.services.document_loader import DocumentLoader
except ImportError:  # pragma: no cover - safe fallback when class isn't available
    DocumentLoader = None


logger = logging.getLogger(__name__)


def _classify_topic(query: str, classifier: TopicClassifier) -> str:
    """Classify a student query into a topic."""
    try:
        return classifier.classify_question(query)
    except Exception as exc:
        logger.exception("Topic classification failed: %s", exc)
        return "general"


def _load_source_documents(user_id: str, topic: str, query: str) -> List[str]:
    """Load supporting documents using available document loader interfaces."""
    if DocumentLoader is None:
        logger.warning("DocumentLoader is unavailable; returning empty source docs")
        return []

    try:
        loader = DocumentLoader()

        if hasattr(loader, "load_documents"):
            docs = loader.load_documents(user_id=user_id, topic=topic, query=query)
        elif hasattr(loader, "load_relevant_documents"):
            docs = loader.load_relevant_documents(user_id=user_id, topic=topic, query=query)
        else:
            logger.warning("DocumentLoader has no supported loader method")
            docs = []

        if not docs:
            return []

        normalized_docs: List[str] = []
        for doc in docs:
            if isinstance(doc, str):
                normalized_docs.append(doc)
            elif isinstance(doc, dict):
                normalized_docs.append(str(doc.get("content", doc)))
            else:
                normalized_docs.append(str(doc))

        return normalized_docs

    except Exception as exc:
        logger.exception("Document loading failed for user=%s topic=%s: %s", user_id, topic, exc)
        return []


def _translate_query_if_needed(query: str, translator: TranslationService) -> str:
    """Translate incoming query into English if it appears to be in another language."""
    try:
        return translator.translate_text(query, "en")
    except Exception as exc:
        logger.exception("Query translation failed: %s", exc)
        return query


def _choose_response_format(query: str) -> str:
    """Infer expected response format from query text."""
    query_lower = query.lower()

    if "quiz" in query_lower:
        return "quiz"
    if "summary" in query_lower:
        return "summary"
    if "notes" in query_lower:
        return "notes"

    return "explanation"


def _generate_ai_response(query: str, topic: str, source_docs: List[str]) -> str:
    """Generate a structured tutor response using topic and supporting context."""
    response_format = _choose_response_format(query)
    context = source_docs[:2]

    if response_format == "quiz":
        return (
            f"Topic: {topic}\n"
            "Quick Quiz:\n"
            "1) What is the core concept behind this topic?\n"
            "2) Solve one practical example and explain each step.\n"
            "3) What is one common mistake students make?\n"
            f"Reference: {context[0] if context else 'No source document available.'}"
        )

    if response_format == "summary":
        return (
            f"Summary for {topic}:\n"
            f"- Key idea: {query}\n"
            f"- Important points: {context[0] if context else 'Review class notes and definitions.'}\n"
            "- Next step: Practice two applied questions."
        )

    if response_format == "notes":
        return (
            f"Study Notes ({topic})\n"
            f"- Focus question: {query}\n"
            f"- Concept note: {context[0] if context else 'Start from definitions and formulas.'}\n"
            f"- Extra note: {context[1] if len(context) > 1 else 'Add one solved example in your notebook.'}"
        )

    return (
        f"Explanation ({topic}):\n"
        f"Your question: {query}\n"
        f"Guidance: {context[0] if context else 'Break the concept into definitions, formula, and example.'}\n"
        "Tip: Teach the concept back in your own words to verify understanding."
    )


def process_student_query(query: str, user_id: str) -> Dict[str, Any]:
    """
    Process a student query end-to-end for the AI Tutor platform.

    Returns a JSON-serializable dictionary with:
    - topic
    - response_text
    - source_docs
    """
    logger.info("Processing student query for user=%s", user_id)

    if not query or not query.strip():
        logger.error("Received empty query for user=%s", user_id)
        return {
            "topic": "general",
            "response_text": "Please enter a valid question.",
            "source_docs": []
        }

    classifier = TopicClassifier()
    translator = TranslationService()

    translated_query = _translate_query_if_needed(query=query, translator=translator)
    topic = _classify_topic(query=translated_query, classifier=classifier)
    source_docs = _load_source_documents(user_id=user_id, topic=topic, query=translated_query)
    response_text = _generate_ai_response(
        query=translated_query,
        topic=topic,
        source_docs=source_docs
    )

    response_payload = {
        "topic": topic,
        "response_text": response_text,
        "source_docs": source_docs,
    }

    logger.info("Generated response for user=%s with topic=%s", user_id, topic)
    return response_payload
