from backend.services.rag_engine import RAGEngine


class MentorAI:
    def __init__(self, rag_engine: RAGEngine) -> None:
        self.rag = rag_engine

    def respond(self, user_id: str, question: str, context: str = "") -> str:
        references = self.rag.retrieve(user_id=user_id, query=question, limit=2)
        source_text = " | ".join(references) if references else "No indexed notes found yet."
        return (
            f"Jarvis Mentor\n"
            f"Question: {question}\n"
            f"Plan: Understand fundamentals, practice examples, then self-test.\n"
            f"Context: {context or 'none'}\n"
            f"RAG context: {source_text}"
        )
