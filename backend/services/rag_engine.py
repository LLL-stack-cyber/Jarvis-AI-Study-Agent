from dataclasses import dataclass, field


@dataclass
class RAGEngine:
    """In-memory baseline retrieval engine for local development."""

    vector_store: dict[str, list[str]] = field(default_factory=dict)

    def ingest_notes(self, user_id: str, raw_text: str, chunk_size: int = 300) -> int:
        normalized = " ".join(raw_text.split())
        chunks = [normalized[i : i + chunk_size] for i in range(0, len(normalized), chunk_size)]
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        self.vector_store.setdefault(user_id, []).extend(chunks)
        return len(chunks)

    def retrieve(self, user_id: str, query: str, limit: int = 3) -> list[str]:
        chunks = self.vector_store.get(user_id, [])
        if not chunks:
            return []

        terms = [t.lower() for t in query.split() if t.strip()]

        def score(chunk: str) -> int:
            c = chunk.lower()
            return sum(1 for term in terms if term in c)

        ranked = sorted(chunks, key=score, reverse=True)
        return ranked[:limit]
